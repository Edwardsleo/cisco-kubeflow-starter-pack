# Malicious Network Traffic Predicton using Pipelines

## What we're going to build

Train and serve Network Traffic model using KF pipeline, and predict flow label for client's data from Jupyter notebook.

![TF-Network Traffic Pipeline](pictures/0-network-graph.PNG)

## Infrastructure Used

* Cisco UCS - C240M5 and C480ML


## Setup

### Upload Notebook file

Upload [Network Traffic-Pipeline-Deployment.ipynb](https://github.com/CiscoAI/cisco-kubeflow-starter-pack/blob/master/apps/networking/network-traffic/onprem/pipelines/Network-Pipeline-Deployment.ipynb)

### Run Network Traffic Pipeline

Open the Network Traffic-Pipeline-Deployment.ipynb file and run pipeline

Clone git repo

![TF-Network Traffic  Pipeline](pictures/1-git-clone.PNG)

Loading Components

![TF-BLERSSI Pipeline](pictures/2-load-compoents.PNG)

Run Pipeline

![TF-Network Traffic Pipeline](pictures/2-run-pipeline.PNG)

Once Network Traffic Pipeline is executed Experiment and Run link will generate and displayed as output

![TF-Network Traffic Pipeline](pictures/3-exp-link.PNG)

Click on latest experiment which is created

![TF-Network Traffic Pipeline](pictures/4-pipeline-created.PNG)

Pipeline components execution can be viewed as below

![TF-Network Traffic Pipeline](pictures/6-pipeline-completed.PNG)


Logs of Network Traffic Training Component

![TF-Network Traffic Pipeline](pictures/2-training.PNG)

Logs of Serving Component

![TF-Network Traffic Pipeline](pictures/3-serving.PNG)

Logs of WebUI Component

![TF-Network Traffic Pipeline](pictures/4-webui.PNG)

Tensorboard Graph for Network Traffic

![TF-Network Traffic Pipeline](pictures/5-tensorboard-graph.PNG)

 Using Web UI - upload test data file located [here](https://github.com/CiscoAI/cisco-kubeflow-starter-pack/blob/master/apps/networking/network-traffic/onprem/data/Network_Test_Traffic.csv)

![TF-Network Traffic Pipeline](pictures/7-upload-file-1.PNG)

 Prediction of Traffic flow label and its probability

![TF-Network Traffic Pipeline](pictures/8-show-table.PNG)
