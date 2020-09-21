# BLERSSI Location Prediction using Kubeflow Pipelines

## What we're going to build

To train, serve and prodict  model  using kubeflow pipeline through jupyter-notebook.

![TF-BLERSSI Pipeline](pictures/0-blerssi-graph.png)

## Infrastructure Used

* Cisco UCS - C240

## Setup

### Upload Notebook file

Upload [BLERSSI-Pipeline-Deployment.ipynb](https://github.com/CiscoAI/cisco-kubeflow-starter-pack/blob/master/apps/networking/ble-localization/onprem/pipelines/BLERSSI-Pipeline-Deployment.ipynb)

### Run BLERSSI Pipeline

Open the BLERSSI-Pipeline-Deployment.ipynb file and run pipeline

Clone git repo

![TF-BLERSSI Pipeline](pictures/1-git-clone.PNG)

Loading Components

![TF-BLERSSI Pipeline](pictures/2-load-compoents.PNG)


Run Pipeline

![TF-BLERSSI Pipeline](pictures/2-run-pipeline.PNG)


Once BLERSSI Pipeline is executed, Experiment and Run link will be generated and displayed as output

![TF-BLERSSI Pipeline](pictures/3-exp-link.PNG)


Click on latest experiment which is created 

![TF-BLERSSI Pipeline](pictures/4-pipeline-created.PNG)


Pipeline components execution can be viewed as below

![TF-BLERSSI Pipeline](pictures/6-pipeline-completed.PNG)


Logs of BLERSSI Training Component

![TF-BLERSSI Pipeline](pictures/2-training.PNG)


Logs of Serving Component

![TF-BLERSSI Pipeline](pictures/3-serving.PNG)


Logs of WebUI Component

![TF-BLERSSI Pipeline](pictures/4-webui.PNG)


Logs of Tensorboard Component

![TF-BLERSSI Pipeline](pictures/5-tensorboard-log.PNG)

For obtaining the URLs for Tensorboard Graph and WebUI for BLERSSI as shown below, change the INGRESS_IP in the last two cells with your ingress IP.

Tensorboard Graph for BLERSSI

![TF-BLERSSI Pipeline](pictures/5-tensorboard-graph.PNG)


Tensorboard Scalar for BLERSSI

![TF-BLERSSI Pipeline](pictures/5-tensorboard-scalar.PNG)


Predict BLERSSI Location using Web UI - upload data file located at [location](https://github.com/CiscoAI/cisco-kubeflow-starter-pack/blob/master/apps/networking/ble-localization/onprem/data/iBeacon_RSSI_Unlabeled_truncated.csv)

![TF-BLERSSI Pipeline](pictures/7-upload-file-1.png)


BLERSSI Prediction Location with Probability

![TF-BLERSSI Pipeline](pictures/8-show-table.PNG)
