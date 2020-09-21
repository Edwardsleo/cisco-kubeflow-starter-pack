import os
import re
import pandas as pd
import numpy as np
import logging
import argparse
import csv
from time import sleep
import kfserving
import tensorflow as tf
from typing import List, Dict
from kfserving import storage
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


import boto3
from botocore.client import Config
import botocore

from kubernetes import client as k8s_client
from kubernetes.client import rest as k8s_rest
from kubernetes import config as k8s_config
from kubernetes.client.rest import ApiException

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


_GCS_PREFIX = "gs://"
_S3_PREFIX = "s3://"


class Upload(object):

    def __init__(self):
        k8s_config.load_incluster_config()
        self.api_client = k8s_client.CoreV1Api()
        self.minio_service_endpoint = None

        self.boto_client = boto3.client('s3',
                      endpoint_url=self.get_minio_endpoint(),
                      aws_access_key_id="minio",
                      aws_secret_access_key="minio123",
                      config=Config(signature_version='s3v4'),
                      region_name="us-east-1",
                      use_ssl=False)


    def get_minio_endpoint(self):

        try:
            self.minio_service_endpoint = self.api_client.read_namespaced_service(name='minio-service', namespace='kubeflow').spec.cluster_ip
            self.minio_service_enpoint_port=self.api_client.read_namespaced_service(name='minio-service', namespace='kubeflow').spec.ports[0].port
        except ApiException as e:
            if e.status == 403:
                logging.warning(f"The service account doesn't have sufficient privileges "
                      f"to get the kubeflow minio-service. "
                      f"You will have to manually enter the minio cluster-ip. "
                      f"To make this function work ask someone with cluster "
                      f"priveleges to create an appropriate "
                      f"clusterrolebinding by running a command.\n"
                      f"kubectl create --namespace=kubeflow rolebinding "
                       "--clusterrole=kubeflow-view "
                       "--serviceaccount=${NAMESPACE}:default-editor "
                       "${NAMESPACE}-minio-view")
                logging.error("API access denied with reason: {e.reason}")

        self.minio_endpoint = "http://"+ self.minio_service_endpoint  + ":%s"%self.minio_service_enpoint_port
        return self.minio_endpoint


    def create_bucket(self, bucket_name):
        try:
            self.boto_client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError:
            bucket = {'Bucket': bucket_name}
            self.boto_client.create_bucket(**bucket)

    def download_file(self, bucket_name, key, filename):

        try:
            self.boto_client.download_file(Bucket=bucket_name, Key=key, Filename=filename)
            mode="a+"
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logging.info("File not exist")
                mode="w+"
        return mode

    def upload_file(self, bucket_name, blob_name, file_to_upload):

        self.boto_client.upload_file(file_to_upload, bucket_name, blob_name)
        return "s3://{}/{}".format(bucket_name, blob_name)


class KFServing(kfserving.KFModel):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        if args.storage_uri.startswith(_GCS_PREFIX) or args.storage_uri.startswith(_S3_PREFIX):
            obj=storage.Storage()
            obj.download(uri=args.storage_uri, out_dir=args.out_dir)
        self.ready = True

    def preprocess(self, request):

        self.input_data=request['instances']
        self.pre=(np.array(self.input_data)/-200)
        request['instances']=self.pre.tolist()
        return request['instances']

    def postprocess(self, request):
        """
        Add your own metrics and push metrics to prometheus pushgateway
        Here we are reading data from 'kfserving_metrics.csv' file and generating metrics
        The Pushgateway allows ephemeral and batch jobs to expose their metrics to Prometheus
        """

        obj=Upload()
        obj.create_bucket(args.bucket_name)
        mode=obj.download_file(args.bucket_name, 'kfserving_metrics.csv', 'kfserving_metrics.csv')
        fieldnames=["b3001", "b3002","b3003","b3004","b3005","b3006","b3007","b3008","b3009","b3010","b3011","b3012","b3013", "class_id", "probabilities"]
        with open('kfserving_metrics.csv', mode) as csvfile:
            writer=csv.DictWriter(csvfile, fieldnames=fieldnames)
            if mode=='w+':
                writer.writeheader()
            row={'class_id': request['class_ids'][0][0], 'probabilities':request['probabilities'][0]}
            for label, value in zip(self.feature_col,self.input_data):
                row.update({label:value})
            writer.writerow(row)

        with open('kfserving_metrics.csv', 'r') as file:
            lines=file.readlines()
        if len(lines)>=100:
            data_frames=pd.read_csv('kfserving_metrics.csv')
            data_frame=data_frames.drop(['class_id','probabilities'], axis=1)
            data_frame=data_frame/-200
            metrics={}
            for feature in fieldnames[:-2]:
                metrics["blerssi_input_data_%s_mean"%feature]=data_frame.mean().to_dict()[feature]
                metrics["blerssi_input_data_%s_min"%feature]=data_frame.min().to_dict()[feature]
                metrics["blerssi_input_data_%s_std"%feature]=data_frame.std().to_dict()[feature]
                metrics["blerssi_input_data_%s_median"%feature]=data_frame.median().to_dict()[feature]

            metrics["blerssi_class_id_mean"]=data_frames['class_id'].mean()
            metrics["blerssi_class_id_min"]=data_frames['class_id'].min()
            metrics["blerssi_class_id_std"]=data_frames['class_id'].std()

            registry = CollectorRegistry()
            for k,v in metrics.items():
                self.push_metrics(k,v, registry)

        obj.upload_file(args.bucket_name, 'kfserving_metrics.csv', 'kfserving_metrics.csv')
        return request

    def push_metrics(self, metric_name, value, registry):

        #push metrics to prometheus pushgateway
        g = Gauge(metric_name, 'blerssi', registry=registry)
        g.set(value)
        push_to_gateway(args.pushgateway, job='blerssi', registry=registry)

    def predict(self, request):

        X=request
        self.feature_col=["b3001", "b3002","b3003","b3004","b3005","b3006","b3007","b3008","b3009","b3010","b3011","b3012","b3013"]

        input={}
        for i in range(len(X)):
            input.update({self.feature_col[i]:[X[i]]})

        for dir in os.listdir(args.out_dir):
            if re.match('[0-9]',dir):
                exported_path=os.path.join(args.out_dir,dir)
                break
        else:
            raise Exception("Model path not found")

        # Open a Session to predict
        with tf.Session() as sess:
            tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], exported_path)
            predictor= tf.contrib.predictor.from_saved_model(exported_path,signature_def_key='predict')
            output_dict= predictor(input)
        sess.close()

        output={}
        output['probabilities']=output_dict['probabilities'].tolist()
        output['class_ids']=output_dict['class_ids'].tolist()
        logging.info("output: %s"%output['class_ids'])
        return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--http_port', default=8081, type=int,
                    help='The HTTP Port listened to by the model server.')
    parser.add_argument('--pushgateway', help='Prometheus pushgateway to push metrics')
    parser.add_argument('--storage_uri', help='storage uri for your model')
    parser.add_argument('--out_dir', help='out dir')
    parser.add_argument('--bucket_name', default='kfserving', help='bucket name to store model metrics')
    args, _ = parser.parse_known_args()
    model = KFServing("blerssi-model")
    model.load()
    kfserving.KFServer(http_port=args.http_port).start([model])
