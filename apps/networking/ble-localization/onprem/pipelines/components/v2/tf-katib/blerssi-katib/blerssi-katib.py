from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import os
import time
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

  args = parser.parse_args()
  return args

def main():
    print("Hello World")
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
        additional_metric_names= ["Train-accuracy"],
        type = "maximize")

    # Parameters
    feasible_space_batchsize = V1alpha3FeasibleSpace(list = ["16","32","48","64"])
    feasible_space_lr = V1alpha3FeasibleSpace(min = "0.01", max = "0.03")

    parameters = [V1alpha3ParameterSpec(
        feasible_space = feasible_space_batchsize,
        name = "--batch-size",
        parameter_type = "categorical"
        ),

    V1alpha3ParameterSpec(
        feasible_space = feasible_space_lr,
        name = "--learning-rate",
        parameter_type ="double"
        )]

    # Trialtemplate
    go_template = V1alpha3GoTemplate(
        raw_template =   "apiVersion: \"batch/v1\"\nkind: Job\nmetadata:\n  name: {{.Trial}}\n  namespace: {{.NameSpace}}\nspec:\n  template:\n    spec:\n      containers:\n      - name: {{.Trial}}\n        image: %s\n        command:\n        - \"python3\"\n        - \"/opt/blerssi-model.py\"\n        {{- with .HyperParameters}}\n        {{- range .}}\n        - \"{{.Name}}={{.Value}}\"\n        {{- end}}\n        {{- end}}\n      restartPolicy: Never"%args.image
        )


    trial_template= V1alpha3TrialTemplate(go_template=go_template)
    timestamp = str(args.timestamp)
    experimentname = "blerssi-"+timestamp
    # Experiment
    experiment = V1alpha3Experiment(
        api_version="kubeflow.org/v1alpha3",
        kind="Experiment",
        metadata=V1ObjectMeta(name=experimentname,namespace="anonymous"),

        spec=V1alpha3ExperimentSpec(
             algorithm = algorithm,
             max_failed_trial_count=3,
             max_trial_count=5,
             objective = objective,
             parallel_trial_count=5,
             parameters = parameters ,
             trial_template = trial_template
        )
    )


    namespace = "anonymous"
    print("NAMEPSACE : ")
    print(namespace)
    kclient = kc.KatibClient()
    kclient.create_experiment(experiment, namespace=namespace)

    result = kclient.get_experiment_status(name=experimentname, namespace=namespace)
    print(result)
    while result != "Succeeded" and  result != "Failed" :
        time.sleep(5)
        result = kclient.get_experiment_status(name=experimentname, namespace=namespace)
        print(result)

    kclient.get_optimal_hyperparmeters(name=experimentname,namespace=namespace)

    parameter = kclient.get_optimal_hyperparmeters(name=experimentname, namespace=namespace)
    batchsize = parameter['currentOptimalTrial']['parameterAssignments'][0]['value']
    learningrate = parameter['currentOptimalTrial']['parameterAssignments'][1]['value']

    print(timestamp)
    if not os.path.exists('/mnt/Model_Blerssi'):
        os.makedirs('/mnt/Model_Blerssi')
    filename = "/mnt/Model_Blerssi/hpv-"+timestamp+".txt"
    f = open(filename, "w")
    f.write(batchsize + "\n")
    f.write(learningrate)
    f.close()

if __name__=="__main__":
    main()
