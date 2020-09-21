# BLERSSI Location Prediction using Kubeflow Pipelines

<!-- vscode-markdown-toc -->
* [What we're going to build](#Whatweregoingtobuild)
    * [Infrastructure Used](#InfrastructureUsed)
* [Prerequisites](#Prerequisites)
* [UCS Setup](#UCSSetup)
    * [Install NFS server (if not installed](#InstallNFSserverifnotinstalled)
    * [Retrieve Ingress IP](#RetrieveIngressIP)
    * [Installing NFS server, PVs and PVCs.](#InstallingNFSserverPVsandPVCs.)
    * [Update Seldon Core Operator Crds](#UpdateSeldonCoreOperatorCrds)
* [Pipeline Workflow](#PipelineWorkflow)
    * [Create Jupyter Notebook Server](#CreateJupyterNotebookServer)
    * [Upload Pipeline Notebook](#UploadPipelineNotebook)
    * [Run Pipeline](#RunPipeline)
* [Run A Prediction](#RunAPrediction)
* [CleanUp](#CleanUp)

<!-- vscode-markdown-toc-config
        numbering=false
        autoSave=true
        /vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Whatweregoingtobuild'></a>What we're going to build

To train, serve using kubeflow pipeline and prediction for client request through jupyter-notebook.

![TF-BLERSSI Pipeline](pictures/0-blerssi-graph.PNG)

### <a name='InfrastructureUsed'></a>Infrastructure Used

* Cisco UCS - C240M5 and C480ML

## <a name='Prerequisites'></a>Prerequisites

- [ ] Kubernetes Cluster(UCS) with Kubeflow 1.0 installed

## <a name='UCSSetup'></a>UCS Setup

To install Kubeflow, follow the instructions [here](../../../../../../install)

### <a name="InstallNFSserverifnotinstalled"></a>Install NFS server (if not installed)

To install NFS server follow steps below.

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

#### <a name='InstallingNFSserverPVsandPVCs.'></a>Installing NFS server, PVs and PVCs.

Follow the [steps](./../../install/) to install NFS server, PVs and PVCs.

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
## <a name='PipelineWorkflow'></a>Pipeline Workflow

Once the setup is complete, the following are the steps in the pipeline workflow.

### <a name='CreateJupyterNotebookServer'></a>Create Jupyter Notebook Server

Follow the [steps](./../../notebook#create--connect-to-jupyter-notebook-server) to create & connect to Jupyter Notebook Server in Kubeflow

### <a name='UploadPipelineNotebook'></a>Upload Pipeline Notebook

Upload [BLERSSI-Pipeline-Deployment.ipynb](BLERSSI-Pipeline-Deployment.ipynb)

### <a name='RunPipeline'></a>Run Pipeline

Open the [BLERSSI-Pipeline-Deployment.ipynb](BLERSSI-Pipeline-Deployment.ipynb) file and run pipeline

### Clone git repo

![TF-BLERSSI Pipeline](pictures/1-git-clone.PNG)

### Install required libraries

![TF-BLERSSI Pipeline](pictures/2-install-libraries.PNG)

### Restart kernel

![TF-BLERSSI Pipeline](pictures/3-restart-kernal.PNG)

### Import libraries

![TF-BLERSSI Pipeline](pictures/4-import-libraries.PNG)

### Component files Declarations

![TF-BLERSSI Pipeline](pictures/5-component-declaration.PNG)

### Adding a new inference server

![TF-BLERSSI Pipeline](pictures/6-adding-inference-service.PNG)

![TF-BLERSSI Pipeline](pictures/6-adding-inference-service1.PNG)

### Loading Components

![TF-BLERSSI Pipeline](pictures/2-load-compoents.PNG)

![TF-BLERSSI Pipeline](pictures/9-define-pv-pvc.PNG)

### Define SeldonDeployment

![TF-BLERSSI Pipeline](pictures/8-define-seldon-spec.PNG)

### Define pipeline function

Define BLERSSI pipeline function and create Experiment and Run

![TF-BLERSSI Pipeline](pictures/10-run-pipeline.PNG)

### Click on latest experiment which is created 

![TF-BLERSSI Pipeline](pictures/4-pipeline-created.PNG)

### Pipeline components execution can be viewed as below

![TF-BLERSSI Pipeline](pictures/18-pipeline-completed.PNG)

### Logs of BLERSSI katib component

![TF-BLERSSI Pipeline](pictures/19-katib-logs.PNG)

### Logs of BLERSSI Training Component

![TF-BLERSSI Pipeline](pictures/20-training-logs.PNG)

### Logs of Seldon deploy Component

![TF-BLERSSI Pipeline](pictures/21-seldon-serving-logs.PNG)

## <a name='RunAPrediction'></a>Run a Prediction

Before run a prediction, make sure that Pipeline Run is Complete in the Dashboard

![TF-BLERSSI Pipeline](pictures/11-check-seldon-running.PNG)

### Wait for state to become available

![TF-BLERSSI Pipeline](pictures/12-wait-for-state-available.PNG)

### Test data for prediction

![TF-BLERSSI Pipeline](pictures/14-test-data.PNG)

### Predict location for test data using served BLERSSI Model

![TF-BLERSSI Pipeline](pictures/15-run-prediction.PNG)

### Prediction of the model and explain

![TF-BLERSSI Pipeline](pictures/16-run-explainer.PNG)

## <a name='CleanUp'></a>Clean Up

### Delete the InferenceService

![TF-BLERSSI Pipeline](pictures/17-delete-seldon-dep.PNG)
