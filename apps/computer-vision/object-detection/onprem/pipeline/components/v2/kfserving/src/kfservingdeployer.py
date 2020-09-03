import os
import re
import time
import argparse
from kubernetes.client import V1Container
from kfserving import KFServingClient
from kfserving import constants
from kfserving import utils
from kfserving import V1alpha2EndpointSpec
from kfserving import V1alpha2PredictorSpec
from kfserving import V1alpha2InferenceServiceSpec
from kfserving import V1alpha2InferenceService
from kfserving import V1alpha2CustomSpec

from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from kubernetes.client.rest import ApiException

k8s_config.load_incluster_config()
def main():

    api_version = constants.KFSERVING_GROUP + '/' + constants.KFSERVING_VERSION
    default_endpoint_spec = V1alpha2EndpointSpec(
                          predictor=V1alpha2PredictorSpec(
                              custom=V1alpha2CustomSpec(
                                  container=V1Container(
                                      name="kfserving-container",
                                      image=FLAGS.image,
                                      env=[{"name":"STORAGE_URI", "value":"%s"%FLAGS.storage_uri}],
                                      command=["python"],
                                      args=[
                                          "model.py",
                                          "--model-name", "%s"%FLAGS.inference_name,
                                          ]))))

    isvc = V1alpha2InferenceService(api_version=api_version,
                          kind=constants.KFSERVING_KIND,
                          metadata=k8s_client.V1ObjectMeta(
                              name=FLAGS.inference_name, namespace=FLAGS.namespace),
                                spec=V1alpha2InferenceServiceSpec(default=default_endpoint_spec)
                                )
    # Create inference service
    KFServing = KFServingClient()
    KFServing.create(isvc)
    time.sleep(2)

    # Check inference service
    KFServing.get(FLAGS.inference_name, namespace=FLAGS.namespace, watch=True, timeout_seconds=180)

    model_status=KFServing.get(FLAGS.inference_name, namespace=FLAGS.namespace)

    for condition in model_status["status"]["conditions"]:
        if condition['type'] == 'Ready':
            if condition['status'] == 'True':
                print('Model is ready')
                break
            else:
                print('Model is timed out, please check the inferenceservice events for more details.')
                exit(1)
    try:
        print(
            model_status["status"]["url"]
            + " is the knative domain header. $ISTIO_INGRESS_ENDPOINT are defined in the below commands"
        )
        print("Sample test commands: ")
        print(
            "# Note: If Istio Ingress gateway is not served with LoadBalancer, use $CLUSTER_NODE_IP:31380 as the ISTIO_INGRESS_ENDPOINT"
        )
        print(
            "ISTIO_INGRESS_ENDPOINT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
        )
        # model_status['status']['url'] is like http://flowers-sample.kubeflow.example.com/v1/models/flowers-sample
        url=re.compile(r"https?://")
        host, path = url.sub("", model_status["status"]["url"]).split("/", 1)
        print(
            'curl -X GET -H "Host: ' + host + '" http://$ISTIO_INGRESS_ENDPOINT/' + path
        )
    except:
        print("Model is not ready, check the logs for the Knative URL status.")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--inference-name', default="object-detection", type=str,
                    help='Name of the inferenceservice model.')
    parser.add_argument('--storage-uri', default="pvc://nfs/object_detection/model", help="storage uri path")
    parser.add_argument('--image', type=str, help='Inferenceservice custom image')
    parser.add_argument('--namespace', type=str, default="kubeflow",help='In which namespace you want to deploy kfserving')
    FLAGS, _ = parser.parse_known_args()
    main()
