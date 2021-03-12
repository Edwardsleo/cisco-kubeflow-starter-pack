# TensorFlow Object Detection Workflow using Kubeflow Pipeline

Creating accurate machine learning models capable of localizing and identifying multiple objects in a single image remains a core challenge in computer vision. The TensorFlow Object Detection API is an open source framework built on top of TensorFlow that makes it easy to construct, train and deploy object detection models. At Google we’ve certainly found this codebase to be useful for our computer vision needs, and we hope that you will as well.

* Download coco datasets , mobilenet_v2.ckpt , mscoco_label_map.pbtxt and ssd_mobilenet_v2_320x320_coco17_tpu config from object storage.  
* Train an tensorflow object detection model using coco dataset and ssd_mobilenet_v2_320x320_coco17_tpu configuration.
* Convert the checkpoints to tflite and upload to object storage.
* Serve tflite model using Kubeflow pipeline.
* Perform prediction for a client image request through Jupyter-notebook. 

![Object Detection Pipeline](pictures/pipeline.PNG)

## <a name='InfrastructureUsed'></a>**Infrastructure Used**
Cisco UCS - C240M5 and C480ML
## <a name='Prerequisites'></a>**Prerequisites**
* UCS machine with [Kubeflow](https://www.kubeflow.org/) 1.0 installed


## <a name='UCSSetup'></a>**UCS Setup**

* Install Kubeflow from [here](../../../../../../install)
* Install NFS server (if not installed) from [here](../#ucs-setup)
* Create Jupyter Notebook Server from [here](../#create-jupyter-notebook-server)
* Create Kubernetes secret to access S3 from [here](../#create-kubernetes-secret-to-access-s3)

### <a name='UploadNotebookfile'></a>**Upload Object Detection Pipeline Notebook file**

Upload [object-detection-pipeline-deployment-tf2.ipynb](object-detection-pipeline-deployment-tf2.ipynb)

### <a name='RunPipeline'></a>**Run Object Detection Pipeline**

Open the uploaded notebook and start executing cells, screenshots of which are captured below.

![Object Detection Pipeline](pictures/clone.PNG)

![Object Detection Pipeline](pictures/loadpipeline.PNG)

![Object Detection Pipeline](pictures/volumeclaim.PNG)


![Object Detection Pipeline](pictures/pipelinefunc.PNG)

![Object Detection Pipeline](pictures/compile.PNG)

*Once the pipeline is executed, a run link will be generated and displayed. 
If you click the link, you will directed to Kubeflow Pipeline Dashboard*

### <a name='PipelineDashboard'></a>**KF Pipeline Dashboard**

Click on the latest experiment which is created

![Object Detection Pipeline](pictures/experim.PNG)

### Pipeline components screenshots & logs can be viewed as below

#### Tensorboard Component:

![Object Detection Pipeline](pictures/tfboard_comp.PNG)

After the successfull completion of tensorboard component, view the Tensorboard using        
url http://{ingress-ip}:{ingress-ip-port}/{timestamp}/tensorboard/

#### Training component:

![Object Detection Pipeline](pictures/train-comp.PNG)

* Training metrics are tracked in Tensorboard visualization at the time of training

#### Inference component:

Converts checkpoint to tflite inference

![Object Detection Pipeline](pictures/infern_comp.PNG)

### <a name='ModelInference'></a>**Model Inference from Notebook**

Upload [object-detection-inference-tflite.ipynb](object-detection-inference-tflite.ipynb)

#### Dependencies files required
* tflite model
* mscoco_label_map.pbtxt
* mobilenet_v2.ckpt-1.index
* pipeline config (ssd_mobilenet_v2_320x320_coco17_tpu-8.config)

![Object Detection Pipeline](pictures/load-tflite.PNG)

![Object Detection Pipeline](pictures/input_image.PNG)

![Object Detection Pipeline](pictures/result.PNG)












