from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import json
import sys
import tensorflow as tf
import pandas as pd
import numpy as np
import shutil
import os
from sklearn.preprocessing import OneHotEncoder
import time
import calendar
from kubernetes import client as k8s_client
from kubernetes.client import rest as k8s_rest
from kubernetes import config as k8s_config
from kubernetes.client.rest import ApiException
from kubernetes.client import V1PodTemplateSpec
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1PodSpec
from kubernetes.client import V1Container
import kubeflow.katib as kc
from kubeflow.katib import *

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('--image',
                      type=str,
                      help='Training image')
  parser.add_argument('--timestamp',
                      type=str,
                      help='Timestamp value')
  parser.add_argument('--batchsize',
                      type=int,
                      default=32,
                      help='The number of batch size during training')
  parser.add_argument('--learningrate',
                      type=float,
                      default=0.01,
                      help='Learning rate for training.')

  args = parser.parse_args()
  return args

def main():
    
    args = parse_arguments()
    algorithmsettings = V1alpha3AlgorithmSetting(
        name= "random_state",
        value = "10"
        )
    algorithm = V1alpha3AlgorithmSpec(
        algorithm_name = "random",
        algorithm_settings = [algorithmsettings]
      )

    # Metric Collector
    collector = V1alpha3CollectorSpec(kind = "TensorFlowEvent")
    FileSystemPath = V1alpha3FileSystemPath(kind = "/train" , path = "Directory")
    metrics_collector_spec = V1alpha3MetricsCollectorSpec(
        collector = collector,
        source = FileSystemPath)

    # Objective
    objective = V1alpha3ObjectiveSpec(
        goal = 0.5,
        objective_metric_name = "accuracy",
        additional_metric_names= ["loss"],
        type = "maximize")

    # Parameters
    feasible_space_batchsize = V1alpha3FeasibleSpace(list = ["16","32","48","64"])
    feasible_space_lr = V1alpha3FeasibleSpace(min = "0.01", max = "0.03")

    parameters = [V1alpha3ParameterSpec(
        feasible_space = feasible_space_batchsize,
        name = "--batchsize",
        parameter_type = "categorical"
        ),

    V1alpha3ParameterSpec(
        feasible_space = feasible_space_lr,
        name = "--learningrate",
        parameter_type ="double"
        )]

    # Trialtemplate
    go_template = V1alpha3GoTemplate(
        raw_template = "apiVersion: batch/v1\nkind: Job\nmetadata:\n  name: {{.Trial}}\n  namespace: {{.NameSpace}}\nspec:\n  template:\n    spec:\n      containers:\n      - name: {{.Trial}}\n        image: %s\n        command:\n        - \"python\"\n        - \"/opt/covid-xray-katib.py\"\n        {{- with .HyperParameters}}\n        {{- range .}}\n        - \"{{.Name}}={{.Value}}\"\n        {{- end}}\n        {{- end}}\n        resources:\n          limits:\n            nvidia.com/gpu: 1\n        volumeMounts:\n          - mountPath: \"/mnt\"\n            name: \"nfsvolume\"\n      volumes:\n         - name: \"nfsvolume\"\n           persistentVolumeClaim:\n             claimName: \"nfs1\"\n      restartPolicy: Never"%args.image
        )

    trial_template= V1alpha3TrialTemplate(go_template=go_template)
    timestamp = str(args.timestamp)
    experimentname = "chest-xray-"+timestamp
    # Experiment
    experiment = V1alpha3Experiment(
        api_version="kubeflow.org/v1alpha3",
        kind="Experiment",
        metadata=V1ObjectMeta(name=experimentname,namespace="anonymous"),

        spec=V1alpha3ExperimentSpec(
             algorithm = algorithm,
             max_failed_trial_count=3,
             max_trial_count=3,
             objective = objective,
             parallel_trial_count=3,
             parameters = parameters ,
             trial_template = trial_template
        )
    )

    namespace = "anonymous"
    kclient = kc.KatibClient()
    kclient.create_experiment(experiment, namespace=namespace)

    result = kclient.get_experiment_status(name=experimentname, namespace=namespace)
    while result != "Succeeded" and  result != "Failed" :
        time.sleep(5)
        result = kclient.get_experiment_status(name=experimentname, namespace=namespace)
        print(result)

    kclient.get_optimal_hyperparmeters(name=experimentname,namespace=namespace)
    parameter = kclient.get_optimal_hyperparmeters(name=experimentname, namespace=namespace)
    batchsize = parameter['currentOptimalTrial']['parameterAssignments'][0]['value']
    learningrate = parameter['currentOptimalTrial']['parameterAssignments'][1]['value']

    if not os.path.exists('/mnt/Model_Covid'):
        os.makedirs('/mnt/Model_Covid')

    if not os.path.exists('/mnt/Model_Covid/models'):
        os.makedirs('/mnt/Model_Covid/models')

    filename = "/mnt/Model_Covid/hpv-"+timestamp+".txt"
    f = open(filename, "w")
    f.write(batchsize + "\n")
    f.write(learningrate)
    f.close()

if __name__=="__main__":
    main()
