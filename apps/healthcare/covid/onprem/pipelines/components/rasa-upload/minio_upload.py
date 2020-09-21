from kubernetes import client as k8s_client
from kubernetes.client import rest as k8s_rest
from kubernetes import config as k8s_config

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import argparse
import os
import tarfile


class MinioUploader(object):
    def __init__(self, minio_secret, minio_secret_key, region_name):

        k8s_config.load_incluster_config()
        self.api_client = k8s_client.CoreV1Api()
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
        print("minio endopoint : ", self.minio_endpoint)
        self.client = boto3.client('s3',
                                   endpoint_url=self.minio_endpoint,
                                   aws_access_key_id=minio_secret,
                                   aws_secret_access_key=minio_secret_key,
                                   config=Config(signature_version='s3v4'),
                                   region_name=region_name,
                                   use_ssl=False)

    def create_bucket(self, bucket_name):
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            bucket = {'Bucket': bucket_name}
            self.client.create_bucket(**bucket)

    def upload_to_bucket(self, blob_name, bucket_name, file_to_upload):
        self.create_bucket(bucket_name)
        self.client.upload_file(file_to_upload, bucket_name, blob_name)
        return "s3://{}/{}".format(bucket_name, blob_name)

    def flatten(tarinfo):
        tarinfo.name = os.path.basename(tarinfo.name)
        return tarinfo

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('--minio-bucket', type=str, default='rasa', help='minio bucket name')
  parser.add_argument('--minio-username', type=str, default='minio', help='minio secret name')
  parser.add_argument('--minio-key', type=str, default='minio123', help='minio secret key')
  parser.add_argument('--minio-region', type=str, default='us-east-1', help='minio region')
  parser.add_argument('--model-name', type=str, default='rasa_model', help='trained model name')
  parser.add_argument('--model-path', type=str, default='/mnt/models', help='trained model path')

  FLAGS, unparsed = parser.parse_known_args()
  #model_name=FLAGS.model_name + '.tar.gz'
  #file_to_upload=FLAGS.model_path + '/' + model_name
  minio_uploader = MinioUploader(minio_secret=FLAGS.minio_username, minio_secret_key=FLAGS.minio_key, region_name=FLAGS.minio_region)
  tar = tarfile.open("models.tar.gz", "w:gz")
  tar.add(FLAGS.model_path, arcname=os.path.basename("model"))
  tar.close()
  minio_uploader.upload_to_bucket("models.tar.gz", FLAGS.minio_bucket, "models.tar.gz")
  print("uploaded successfully")
