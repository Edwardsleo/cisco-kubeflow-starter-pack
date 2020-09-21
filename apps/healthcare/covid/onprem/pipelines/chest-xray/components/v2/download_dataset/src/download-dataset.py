#Python script to download the uploaded data from minIO into nfs

import argparse
import os
import logging
from zipfile import ZipFile
from minio import Minio
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from kubeflow.fairing.cloud.k8s import MinioUploader

parser = argparse.ArgumentParser()

parser.add_argument('--minio-bucket-name',
                      type=str,
                      help='Name of MinIO bucket where datasets are already uploaded')

args = parser.parse_args()



k8s_config.load_incluster_config()
api_client = k8s_client.CoreV1Api()
minio_service_endpoint = None

#Connect to MinIO service using credentials
try:
    minio_service_endpoint = api_client.read_namespaced_service(name='minio-service', namespace='kubeflow').spec.cluster_ip
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

s3_endpoint = minio_service_endpoint
s3_endPoint = s3_endpoint+":9000"
minio_endpoint = "http://"+s3_endPoint
minio_username = "minio"
minio_key = "minio123"
minio_region = "us-east-1"
print(minio_endpoint)

#Define MinIO uploader
minio_uploader = MinioUploader(endpoint_url=minio_endpoint, minio_secret=minio_username, minio_secret_key=minio_key, region_name=minio_region)

#Create a MinIO client object
minioClient = Minio(s3_endPoint,
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)
#Retrieve objects keys for MinIO objects in MinIO bucket
list_response = minio_uploader.client.list_objects(Bucket=args.minio_bucket_name)
obj_key = list_response['Contents'][0]['Key']

#Download the image dataset zip files from MinIO bucket
minioClient.fget_object(args.minio_bucket_name, obj_key, 'dataset_dl.zip')

#Extract the zip files and store under the same directory 
with ZipFile('dataset_dl.zip', 'r') as zipObj:
   # Extract all the contents of covid zip file into "image_dataset" directory
   zipObj.extractall('/mnt/dataset')
    
    
