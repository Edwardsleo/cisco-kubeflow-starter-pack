##Python script to create tfjob for training object detection model

#Import libraries
from kubernetes.client import V1PodTemplateSpec
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1PodSpec
from kubernetes.client import V1Container
from kubernetes.client import V1VolumeMount
from kubernetes.client import V1Volume
from kubernetes.client import V1PersistentVolumeClaimVolumeSource
from kubernetes.client import V1ResourceRequirements
from kubeflow.tfjob import constants
from kubeflow.tfjob import utils
from kubeflow.tfjob import V1ReplicaSpec
from kubeflow.tfjob import V1TFJob
from kubeflow.tfjob import V1TFJobSpec
from kubeflow.tfjob import TFJobClient
import argparse
import time
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config

def parse_arguments():


        parser = argparse.ArgumentParser()

        # Add the arguments to the parser
        parser.add_argument("--training_image", help="Name of training image")

        parser.add_argument("--timestamp", help='timestamp')

        parser.add_argument("--nfs_path", help='Common NFS path')

        parser.add_argument("--data_dir", help="Path of dataset folder")

        parser.add_argument("--image_list_file", help="Name of image list file")

        parser.add_argument("--darknet_weights", help="Name of darknet weights file")

        parser.add_argument("--converted_weights", help="Name of converted weights in .tf format")

        parser.add_argument("--num_classes", help="Number of object classes")

        parser.add_argument("--dataset", help="image name")

        parser.add_argument("--classes_file", help="Name of object classes file")

        parser.add_argument("--transfer", help="Type of transfer learning used")

        parser.add_argument("--input_size", help="Size of input image")

        parser.add_argument("--epochs", help="epochs")

        parser.add_argument("--batch_size", help="batch size")

        parser.add_argument("--learning_rate", help="learning rate")

        parser.add_argument("--saved_model_dir", help="Output directory to save trained model files")

        parser.add_argument("--samples", help="Number of input samples/images")


        args = parser.parse_args()
        return args

args = parse_arguments()

k8s_config.load_incluster_config()
custom_api=k8s_client.CustomObjectsApi()
namespace = utils.get_default_target_namespace()

#Define tfjob configuration in .JSON format
tfjob = {
   "apiVersion": "kubeflow.org/v1",
   "kind": "TFJob",
   "metadata": {
      "name": "object-detection%s"%args.timestamp,
      "namespace": "%s"%namespace
   },
   "spec": {
      "cleanPodPolicy": "None",
      "tfReplicaSpecs": {
         "Worker": {
            "replicas": 3,
            "restartPolicy": "Never",
            "template": {
               "spec": {
                  "containers": [
                     {
                        "name": "tensorflow",
                        "image": "%s"%args.training_image,
                        "command":['/bin/bash'],
                        "args":["/opt/main.sh",
                                 "--nfs_path",
                                 args.nfs_path,
                                 "--data_dir",
                                 args.data_dir,
                                 "--image_list_file",
                                 args.image_list_file,
                                 "--darknet_weights",
                                 args.darknet_weights,
                                 "--converted_weights",
                                 args.converted_weights,
                                 "--num_classes",
                                 args.num_classes,
                                 "--dataset",
                                 args.dataset,
                                 "--classes_file",
                                 args.classes_file,
                                 "--transfer",
                                 args.transfer,
                                 "--input-size",
                                 args.input_size,
                                 "--epochs",
                                 args.epochs,
                                 "--batch_size",
                                 args.batch_size,
                                 "--learning_rate",
                                 args.learning_rate,
                                 "--saved_model_dir",
                                 args.saved_model_dir,
                                 "--samples",
                                 args.samples
                            ],
                        "volumeMounts": [
                           {
                              "mountPath": "/mnt",
                              "name": "training"
                           }
                        ],
                        "resources": {
                           "limits": {
                              "nvidia.com/gpu": 1
                           }
                        }
                     }
                  ],
                  "volumes": [
                     {
                        "name": "training",
                        "persistentVolumeClaim": {
                           "claimName": "nfs"
                        }
                     }
                  ]
               }
            }
         }
      }
   }
}


tfjob_name=tfjob["metadata"]["name"]

#Create TFJob for training
custom_api.create_namespaced_custom_object(group="kubeflow.org", version="v1", namespace=namespace, plural="tfjobs", body=tfjob)
print("TFjob %s created successfully"%tfjob_name)
time.sleep(20)

status=False
while True:
    conditions = custom_api.get_namespaced_custom_object_status(group="kubeflow.org", version="v1", namespace=namespace, plural="tfjobs", name=tfjob_name)["status"]["conditions"]
    for i in range(len(conditions)):
        if (conditions[i]['type'])=='Succeeded':
            status=True
            print("TFJob Status: %s"%conditions[i]['type'])
            break
        
    if status:
        break
    print("TFJob Status: %s"%conditions[i]['type'])
    time.sleep(60)
