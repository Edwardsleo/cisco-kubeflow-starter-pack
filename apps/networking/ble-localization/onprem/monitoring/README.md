# Monitoring

<!-- vscode-markdown-toc -->
* [What we're going to build](#Whatweregoingtobuild)
    * [Infrastructure Used](#InfrastructureUsed)
* [Prerequisites](#Prerequisites)
* [UCS Setup](#UCSSetup)
    * [Retrieve Ingress IP](#RetrieveIngressIP)
* [Notebook Workflow](#NotebookWorkflow)
    * [Create Jupyter Notebook Server](#CreateJupyterNotebookServer)
    * [Upload Notebook](#UploadNotebook)
    * [Run Notebook](#RunNotebook)
* [Accessing Metrics](#AccessingMetrics)
    * [Prometheus](#Prometheus)
    * [Grafana](#Grafana)
* [CleanUp](#CleanUp)

<!-- vscode-markdown-toc-config
        numbering=false
        autoSave=true
        /vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Whatweregoingtobuild'></a>What we're going to build

Train & save a BLERSSI location model from Kubeflow Jupyter notebook. Then, serve and predict using the saved model and push model i/p and o/p metrics into prometheus

### <a name='InfrastructureUsed'></a>Infrastructure Used

* Cisco UCS - C240

## <a name='Prerequisites'></a>Prerequisites

- [ ] Kubernetes Cluster(GKE, UCS) with Kubeflow 1.0 installed

## <a name='UCSSetup'></a>UCS Setup

To install Kubeflow, follow the instructions [here](../../../../../install)

### <a name='RetrieveIngressIP'></a>Retrieve Ingress IP

For installation, we need to know the external IP of the 'istio-ingressgateway' service. This can be retrieved by the following steps.

```
kubectl get service -n istio-system istio-ingressgateway
```

If your service is of LoadBalancer Type, use the 'EXTERNAL-IP' of this service.

Or else, if your service is of NodePort Type - run the following command:

```
kubectl get nodes -o wide
```

Use either of 'EXTERNAL-IP' or 'INTERNAL-IP' of any of the nodes based on which IP is accessible in your network.

This IP will be referred to as INGRESS_IP from here on.

## <a name='NotebookWorkflow'></a>Notebook Workflow
Once the setup is complete, the following are the steps in the Notebook
workflow.

### <a name='CreateJupyterNotebookServer'></a>Create Jupyter Notebook Server

Follow the [steps](./../notebook#create--connect-to-jupyter-notebook-server) to create & connect to Jupyter Notebook Server in Kubeflow

### <a name='UploadNotebook'></a>Upload Notebook

Upload [monitoring.ipynb](monitoring.ipynb) file to the created Notebook server.

### <a name='RunNotebook'></a>Run Notebook

Open the [monitoring.ipynb](monitoring.ipynb) file and run Notebook

Clone git repo

![BLERSSI KNATIVE METRICS](./pictures/1-git-clone.PNG)

Install required libraries

![BLERSSI KNATIVE METRICS](./pictures/2-install-libraries.PNG)

Restart kernel

![BLERSSI KNATIVE METRICS](./pictures/3-restart-kernal.PNG)

Import libraries

![BLERSSI KNATIVE METRICS](./pictures/4-import-libraries.PNG)

Install Prometheus and Grafana

```
kubectl create namespace knative-monitoring
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.15.0/monitoring-metrics-prometheus.yaml
```
![BLERSSI KNATIVE METRICS](./pictures/5-install-prom-grafana.PNG)

Deploy the Prometheus Pushgateway

![BLERSSI KNATIVE METRICS](./pictures/6-deploy-prom-pushgateway.PNG)

Declare Variables

![BLERSSI KNATIVE METRICS](./pictures/7-declare-variables.PNG)

Definition of Serving Input Receiver Function

![BLERSSI KNATIVE METRICS](./pictures/8-input-receiver-fun.PNG)

Train BLERSSI model

![BLERSSI KNATIVE METRICS](./pictures/9-train-model.PNG)

Once training completes, the model will be stored in local notebook server

![BLERSSI KNATIVE METRICS](./pictures/9-train-model1.PNG)

Get Prometheus Pushgateway cluster IP to push metrics

![BLERSSI KNATIVE METRICS](./pictures/10-get-prom-pushgateway-ip.PNG)

To add your [metrics](./model-server/model.py#L115), [build](./model-server/Dockerfile) the docker image and push into your Docker Hub. It will be used when creating the InferenceService

Inference Logger

Create a message dumper knative service to print out CloudEvents it receives

![BLERSSI KNATIVE METRICS](./pictures/inference-logger.PNG)

Create the InferenceService using KFServing client SDK

Replace docker image with your docker image

![BLERSSI KNATIVE METRICS](./pictures/replace-docker-image.png)

Define InferenceService

![BLERSSI KNATIVE METRICS](./pictures/11-define-isvc.PNG)

Create the InferenceService

![BLERSSI KNATIVE METRICS](./pictures/12-create-isvc.PNG)

Predict location for test data using served BLERSSI Model

![BLERSSI KNATIVE METRICS](./pictures/13-env-variables.PNG)

![BLERSSI KNATIVE METRICS](./pictures/14-test-data.PNG)

![BLERSSI KNATIVE METRICS](./pictures/15-prediction.PNG)

Check the logs of the message dumper

![BLERSSI KNATIVE METRICS](./pictures/inference-request-response-logs.PNG)

## <a name='AccessingMetrics'></a>Accessing Metrics

### <a name='Prometheus'></a>Prometheus

* To open Prometheus, enter the following command

```
kubectl port-forward -n knative-monitoring \
$(kubectl get pods -n knative-monitoring \
--selector=app=prometheus --output=jsonpath="{.items[0].metadata.name}") \
9090
```
* This starts a local proxy of Prometheus on port 9090. For security reasons, the Prometheus UI is exposed only within the cluster.

* Navigate to the Prometheus UI at http://localhost:9090

![BLERSSI KNATIVE METRICS](./pictures/16-prometheus-ds.PNG)

![BLERSSI KNATIVE METRICS](./pictures/17-prometheus-metrics.PNG)

![BLERSSI KNATIVE METRICS](./pictures/17-prometheus-metrics1.PNG)

![BLERSSI KNATIVE METRICS](./pictures/17-prometheus-metrics2.PNG)

### <a name='Grafana'></a>Grafana

* To open Grafana, enter the following command
```
kubectl port-forward --namespace knative-monitoring \
$(kubectl get pods --namespace knative-monitoring \
--selector=app=grafana --output=jsonpath="{.items..metadata.name}") \
3000
```
* This starts a local proxy of Grafana on port 3000. For security reasons, the Grafana UI is exposed only within the cluster.
* Navigate to the Grafana UI at http://localhost:3000
* Select the Home button on the top of the page to see the list of pre-installed dashboards

![BLERSSI KNATIVE METRICS](./pictures/20-pre-listed-ds.PNG)

* Select knative Serving-Scaling Debugging

![BLERSSI KNATIVE METRICS](./pictures/21-grafana-knative.PNG)

![BLERSSI KNATIVE METRICS](./pictures/21-grafana-request.PNG)

* Resource Usages

![BLERSSI KNATIVE METRICS](./pictures/22-resource-usage.PNG)


### <a name='CleanUp'></a>Clean Up

Delete the InferenceService

![BLERSSI KNATIVE METRICS](./pictures/23-delete-isvc.PNG)

Delete the Prometheus pushgateway deployment and service

![BLERSSI KNATIVE METRICS](./pictures/24-delete-pushgateway.PNG)

Uninstall Prometheus and Grafana

![BLERSSI KNATIVE METRICS](./pictures/25-uninstall-prom-grafana.PNG)

Delete Minio Bucket
![BLERSSI KNATIVE METRICS](./pictures/26-delete-minio-bucket.PNG)
