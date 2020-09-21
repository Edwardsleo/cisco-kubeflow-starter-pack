# BLERSSI Location Prediction 

## What we're going to do

Train & save a BLERSSI location model from Kubeflow Jupyter notebook.
Then, serve and predict using the saved model.

### Infrastructure used

* Cisco UCS - C240M5 and C480ML

## Setup

### Retrieve Ingress IP

We need to know the external IP of the 'istio-ingressgateway' service. This can be retrieved by the following steps.

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

### Create & connect to Jupyter Notebook server

You can access Kubeflow Dashboard using the Ingress IP and _31380_ port. For example, http://<INGRESS_IP:31380>

Select _anonymous_ namespace and click Notebook Servers in the left panel of the Kubeflow Dashboard


![TF-BLERSSI Pipeline](pictures/1-kubeflow-ui.PNG)

Click New Server button and provide required details 

![TF-BLERSSI Pipeline](pictures/2-create-notebook.PNG)

Provide Notebook Server name and select notebook image appropriately as below
     
     CPU  - gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-cpu:1.0.0
     GPU  - gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-gpu:1.0.0

![TF-BLERSSI Pipeline](pictures/create-notebook-1.PNG)

Create new Workspace volume

![TF-BLERSSI Pipeline](pictures/create-notebook-2.PNG)

If you are creating GPU attached notebook then choose number of GPUs and GPU Vendor as *NVIDIA*. 

Click Launch button

![TF-BLERSSI Pipeline](pictures/create-notebook-3.PNG)

Once Notebook Server is created, click on Connect button.

![TF-BLERSSI Pipeline](pictures/6-connect-notebook1.PNG)

### Upload BLERSSI-classification.ipynb file

Upload the [BLERSSI-classification.ipynb](./BLERSSI-classification.ipynb) to the Notebook Server.

![TF-BLERSSI Pipeline](pictures/7-upload-pipeline-notebook1.png)

### Train BLERSSI model

Open the notebook file and run commands to train & save BLERSSI model.

![TF-BLERSSI Pipeline](pictures/1-start-training.png)

Once training completes, the model will be stored in the notebook server locally.

![TF-BLERSSI Pipeline](pictures/2-complete-training.png)

### Serve BLERSSI model from chosen model store (MinIO/Workspace Volume) through Kfserving

![TF-BLERSSI Pipeline](pictures/4-create-kfserving-blerssi1.png)

![TF-BLERSSI Pipeline](pictures/4-create-kfserving-blerssi2.png)

### Predict location for test data using served BLERSSI model 

Change Ingress IP in the curl command to your provided value before executing location prediction.


![TF-BLERSSI Pipeline](pictures/5-predict-model.PNG)

Prediction - class_ids(38) in response is location and predicted using kubeflow-kfserving which represents the location "M05"


