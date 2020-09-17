# **Custom HP tuning with Katib for Object Detection Pipeline**

## <a name='Introduction'></a>**Introduction**

Currently, Katib Hyperparameter tuning (HP) for object detection pipeline is done considering two parameters:

* Momentum
* Decay

The hyperparameters and the number of hyperparameters to be tuned can be modified as per requirement. 

## <a name='Procedure'></a>**Custom HP Tuning Procedure**

- Open the source component deployment shell script named ```deploy.sh``` present in the ```src``` folder of [Katib component](./components/v2/katib).

- Add the part of YAML configuration required for the new desired hyperparameter under the ```parameters``` tag similar to the existing as shown below:

![Custom HP tuning](22-katib-params.png)

- Declare the desired hyperparameters as ```do while``` cases of the same file as shown.

![Custom HP tuning](23-katib-params.png)

- Open the ```components.yaml``` of [Katib component](./components/v2/katib), and add the required configuration under the ```inputs:``` tag & the ```args:``` tag under ```implementation:``` as shown.

![Custom HP tuning](24-katib-comp-yaml.png)

- Build Docker image for [Katib component](./components/v2/katib) & provide the image name in the ```component.yaml``` in the location as shown above.

Katib component with customized HP tuning is ready to be used in your Object detection pipeline.
