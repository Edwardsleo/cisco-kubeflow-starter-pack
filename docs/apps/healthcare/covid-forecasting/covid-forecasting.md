# COVID-19 Forecasting using Kubeflow Pipelines

## What we're going to build

To train, serve a COVID model using Kubeflow Pipeline and get prediction for client request through Jupyter notebook.

![COVID Pipeline](./pictures/0-covid-pipeline.PNG)

## Infrastructure Used

* Cisco UCS - C240M5 and C480ML

### Upload Notebook file

Upload [COVID-Pipeline-Deployment.ipynb](https://github.com/CiscoAI/cisco-kubeflow-starter-pack/blob/master/apps/healthcare/covid-forecasting/onprem/pipelines/COVID_Pipeline_Deployment.ipynb)

### Run COVID Pipeline

Open the COVID-Pipeline-Deployment.ipynb file and run pipeline

Clone git repo

![COVID Pipeline](./pictures/1-clone-repo.PNG)

Load The Components

![COVID Pipeline](./pictures/2-load-components.PNG)


Define the COVID Pipeline Function

![COVID Pipeline](./pictures/3-def-pipline-fn.PNG)


Once COVID Pipeline is executed, Experiment and Run link will be generated and displayed as output

![COVID Pipeline](pictures/4-run-pipeline.PNG)


Click on latest experiment which is created 

![TF-COVID Pipeline](./pictures/5-latest-experimnt.png)


Pipeline components execution can be viewed as below.

Logs of COVID Preprocessing Component

![TF-COVID Pipeline](./pictures/6-covid-preprocess.PNG)


Logs of COVID Training Component

![TF-COVID Pipeline](./pictures/7-covid-train.PNG)


Logs of COVID TF Serving Component

![TF-COVID Pipeline](./pictures/8-covid-serve.PNG)

Once pipeline execution is completed return to notebook and execute next cell

Pre-process prediction dataset

![TF-COVID Pipeline](./pictures/10-preprocessing-prediction.PNG)

Make a REST API invocation to serving endpoint for prediction

![TF-COVID Pipeline](./pictures/11-predict-tf-serving.PNG)

Post-processing on the prediction

![TF-COVID Pipeline](./pictures/12-concatenate-data.PNG)

Forecast Table with confirmed Cases

![TF-COVID Pipeline](./pictures/13-Forecasted-table.PNG)

Plot predicted cases in upcoming days

![TF-COVID Pipeline](./pictures/14-graph-of-confirmed.PNG)
