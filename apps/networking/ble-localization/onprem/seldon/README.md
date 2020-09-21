# Seldon Serving and Explainer for BLERSSI Location Prediction

<!-- vscode-markdown-toc -->
* [What we're going to build](#Whatweregoingtobuild)
    * [Infrastructure Used](#InfrastructureUsed)
* [Prerequisites](#Prerequisites)
* [UCS Setup](#UCSSetup)
    * [Update Seldon Core Operator Crds](#UpdateSeldonCoreOperatorCrds)
    * [Retrieve Ingress IP](#RetrieveIngressIP)
* [Notebook Workflow](#NotebookWorkflow)
    * [Create Jupyter Notebook Server](#CreateJupyterNotebookServer)
    * [Upload Notebook](#UploadNotebook)
    * [Run Notebook](#RunNotebook)
* [CleanUp](#CleanUp)

<!-- vscode-markdown-toc-config
        numbering=false
        autoSave=true
        /vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Whatweregoingtobuild'></a>What we're going to build

Train & save a BLERSSI location model from Kubeflow Jupyter notebook. Then, serve and predict using the saved model and explain the predictions of model.

### <a name='InfrastructureUsed'></a>Infrastructure Used

* Cisco UCS - C240

## <a name='Prerequisites'></a>Prerequisites

- [ ] Kubernetes Cluster(UCS) with Kubeflow 1.0 installed

## <a name='UCSSetup'></a>UCS Setup

To install Kubeflow, follow the instructions [here](../../../../../install)

### <a name='UpdateSeldonCoreOperatorCrds'></a>Update Seldon Core Operator Crds

If you are using kubeflow 1.0, then update latest seldon core operator crds.

* Install kustomize

```
curl -s "https://raw.githubusercontent.com/\
kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
export PATH=$PATH:$PWD
```
* Delete existing seldon crds

```
USAGE: kustomize build <<path-to-seldon-core-operator-base>> | kubectl delete -f -
EXAMPLE: kustomize build cisco-kubeflow-starter-pack/install/kf-app/kustomize/seldon-core-operator/base/ | kubectl delete -f -
```
* Install seldon crds

```
git clone -b v1.1-branch https://github.com/kubeflow/manifests.git
USAGE: kustomize build <<path-to-seldon-core-operator-base>> | kubectl apply -f -
EXAMPLE: kustomize build manifests/seldon/seldon-core-operator/base/ | kubectl apply -f -
```

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

Upload [blerssi-seldon.ipynb](blerssi-seldon.ipynb) file to the created Notebook server.

### <a name='RunNotebook'></a>Run Notebook

Open the [blerssi-seldon.ipynb](blerssi-seldon.ipynb) file and run Notebook

### Clone git repo

![BLERSSI SELDON](./pictures/1-git-clone.PNG)

### Install required libraries

![BLERSSI SELDON](./pictures/2-install-libraries.PNG)

### Restart kernel

![BLERSSI SELDON](./pictures/3-restart-kernal.PNG)

### Import libraries

![BLERSSI SELDON](./pictures/4-import-libraries.PNG)

### Get Current k8s Namespace

![BLERSSI SELDON](./pictures/5-get-current-namespace.PNG)

### Declare Variables

![BLERSSI SELDON](./pictures/6-declare-variables.PNG)

### Definition of Serving Input Receiver Function

![BLERSSI SELDON](./pictures/7-input-receiver-fun.PNG)

### Train BLERSSI model

![BLERSSI SELDON](./pictures/8-train-model.PNG)

### Once training completes, the model will be stored in local notebook server

![BLERSSI SELDON](./pictures/8-train-model1.PNG)

### Define Predict Function

![BLERSSI SELDON](./pictures/9-define-custom-fun.PNG)

### Initialize and fit explainer

![BLERSSI SELDON](./pictures/10-initialize-fit-anchor.PNG)
 
### Save Explainer file

![BLERSSI SELDON](./pictures/11-save-explainer.PNG)

### Create a gateway
Create a gateway called kubeflow-gateway in current namespace

![BLERSSI SELDON](./pictures/12-create-gateway.PNG)

To [build](./model-server) the docker image and push into your Docker Hub. It will be used when adding a new inference server

### Adding a new inference server
The list of available inference servers in Seldon Core is maintained in the **seldon-config** configmap, which lives in the same namespace as your Seldon Core operator. In particular, the **predictor_servers** key holds the JSON config for each inference server.

[Refer to for more information](https://docs.seldon.io/projects/seldon-core/en/v1.1.0/servers/custom.html)

![BLERSSI SELDON](./pictures/13-adding-inference-service.PNG)

![BLERSSI SELDON](./pictures/13-adding-inference-service1.PNG)

### Define InferenceService

![BLERSSI SELDON](./pictures/14-seldon-serving-deployment.PNG)

### Create the InferenceService

![BLERSSI SELDON](./pictures/14-seldon-serving-deployment1.PNG)

### Wait for inferenceservice state to become available

![BLERSSI SELDON](./pictures/15-wait-for-become-ready.PNG)

### Predict location for test data using served BLERSSI Model

![BLERSSI SELDON](./pictures/16-env-variables.PNG)

![BLERSSI SELDON](./pictures/17-prediction-request-fun.PNG)

![BLERSSI SELDON](./pictures/18-prediction.PNG)

### Prediction of the model and explain

![BLERSSI SELDON](./pictures/19-explainations.PNG)

## <a name='CleanUp'></a>Clean Up

### Delete a gateway

![BLERSSI SELDON](./pictures/20-delete-gateway.PNG)

### Delete the InferenceService

![BLERSSI SELDON](./pictures/21-delete-seldon-deployment.PNG)

### Delete model and explainer from NB

![BLERSSI SELDON](./pictures/22-delete-model.PNG)
