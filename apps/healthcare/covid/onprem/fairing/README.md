# COVID-19 Forecasting using Kubeflow Fairing 

## What we're going to build

Train & Save a COVID forecast model using Kubeflow Fairing from Jupyter Notebook. Then, deploy the trained model to Kubeflow using Kubeflow Fairing for Predictions.


## Infrastructure used

* Cisco UCS - C240


## Setup


### Create Jupyter notebook server

Follow the [steps](./../notebook#create--connect-to-jupyter-notebook-server) to create & connect to Jupyter Notebook Server in Kubeflow.

### Upload COVID forecast Fairing notebook

Upload the [COVID-Forecast-fairing notebook](./COVID-Forecast-fairing.ipynb) into Jupyter Notebook server in Kubeflow.

![COVID upload](pictures/0_upload_notebook.png)


### Run COVID notebook

Open & run the uploaded COVID-Forecast-fairing.ipynb file.


### Clone Cisco Kubeflow starter pack repository

![COVID Clone](pictures/1_clone_repo.png)


### Configure Docker Registry credentials 

![COVID Configure](pictures/2_configure_docker_credentials.png)

### Create requirements.txt with required python packages

![COVID Create requirements](pictures/3_create_requirements_file.png)

### Import required libraries

![COVID Import Libraries](pictures/4_import_python_libraries.png)

![COVID Setup Fairing](pictures/5_setup_kf_fairing.png)

### Get minio-service cluster IP to upload Docker build context


![COVID Minio Service](pictures/6_minio_service_ip.png)

### Create config-map to map your own docker credentials from created config.json

Note: create configmap named "docker-config". If already exists, delete existing one and create new configmap.

* Delete existing configmap

```
kubectl delete configmap -n $namespace docker-config
```

![COVID Create Configmap](pictures/7_create_configmap.png)

### Define paths for train & test data files

![COVID Define paths](pictures/8_define_paths.png)

### Build docker image for the model
Note: Upload dataset, Dockerfile, and covid-model.py into notebook.
Builder builds training image using input files, an output_map - a map from source location to the location inside the context, and pushes it to the registry.

![COVID Build Docker Image](pictures/9_build_docker_image.png)


### Create Katib experiment
Use Katib for automated tuning of your machine learning (ML) model’s hyperparameters and architecture.

![COVID Create katib experiment](pictures/10_create_katib_experiment.png)

![COVID Create katib experiment](pictures/11_create_katib_experiment1.png)

### Wait for Katib experiment succeeded status

![COVID wait for katib experiment](pictures/12_wait_for_experiment_succeeded.png)

### View the results of the experiment in the Katib UI

[Click here](Katib.md) to view the sample result of Katib experiment.

### Get optimal hyperparameters

![COVID katib experiment trials](pictures/13_get_optimal_hyperparameters.png)


### Add pre-processing function for train data

![COVID Preprocess Train](pictures/14_preprocess_train.png)

### Add pre-processing function for test data

![COVID Preprocess Test](pictures/15_preprocess_test.png)


### Add main pre-processing function

![COVID Preprocess Main](pictures/16_preprocess_main.png)


### Add function for training Model

![COVID Model Train](pictures/17_train_model_function.png)


### Define COVID class to be used by Kubeflow Fairing

Note: Must necessarily contain train() and predict() methods


![COVID Serve](pictures/18_define_covid_serve.png)


### Train COVID model using Kubeflow Fairing

Kubeflow Fairing packages the CovidServe class, the training data, and requirements.txt as a Docker image. 
It then builds & runs the training job on Kubeflow.

![COVID Training](pictures/19_training_using_fairing.png)

### Deploy trained model to Kubeflow for predictions using Kubeflow Fairing

![COVID Deploy model](pictures/20_deploy_trained_model_for_prediction.png)


### Get prediction endpoint

![COVID Predicion Endpoint](pictures/21_get_prediction_endpoint.png)

### Predict for input data using prediction endpoint

![COVID prediction](pictures/22_prediction.png)

### Perform post-processing of prediction result

![COVID postprocessing](pictures/23_postprocessing.png)

### Visualise the final prediction results

![COVID visualise](pictures/24_visualising.png)

### View visualised results as graph

![COVID view graph](pictures/25_view_graph.png)

### Delete prediction endpoint

![COVID Delete endpoint](pictures/26_delete_endpoint.png)



