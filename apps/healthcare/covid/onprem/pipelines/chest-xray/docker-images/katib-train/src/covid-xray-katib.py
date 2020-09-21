from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import AveragePooling2D, AveragePooling3D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from imutils import paths
import numpy as np
import argparse
import cv2
import os
import time
import datetime
import pandas as pd
from tensorflow.keras import backend as K
import tensorflow as tf
import argparse
import os
import logging
from zipfile import ZipFile
from minio import Minio
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from kubeflow.fairing.cloud.k8s import MinioUploader

tf.keras.backend.set_learning_phase(0)
tf.logging.set_verbosity(tf.logging.INFO)
k8s_config.load_incluster_config()
api_client = k8s_client.CoreV1Api()
minio_service_endpoint = None

#Connect to MinIO service using credentials
try:
    minio_service_endpoint = api_client.read_namespaced_service(name='minio-service', namespace='kubeflow').spec.cluster_ip
except ApiException as e:
    if e.status == 403:
        logging.warning(f"The service account doesn't have sufficient privileges "
                      f"to get the kubeflow minio-service. "
                      f"You will have to manually enter the minio cluster-ip. "
                      f"To make this function work ask someone with cluster "
                      f"priveleges to create an appropriate "
                      f"clusterrolebinding by running a command.\n"
                      f"kubectl create --namespace=kubeflow rolebinding "
                       "--clusterrole=kubeflow-view "
                       "--serviceaccount=${NAMESPACE}:default-editor "
                       "${NAMESPACE}-minio-view")
        logging.error("API access denied with reason: {e.reason}")

s3_endpoint = minio_service_endpoint
s3_endPoint = s3_endpoint+":9000"
minio_endpoint = "http://"+s3_endPoint
minio_username = "minio"
minio_key = "minio123"
minio_region = "us-east-1"
print(minio_endpoint)

#Define MinIO uploader
minio_uploader = MinioUploader(endpoint_url=minio_endpoint, minio_secret=minio_username, minio_secret_key=minio_key, region_name=minio_region)

#Create a MinIO client object
minioClient = Minio(s3_endPoint,
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)
#Retrieve objects keys for MinIO objects in MinIO bucket
list_response = minio_uploader.client.list_objects(Bucket='katib-imgzip')
obj_key = list_response['Contents'][0]['Key']

#Download the image dataset zip files from MinIO bucket
minioClient.fget_object('katib-imgzip', obj_key, 'katib_dataset.zip')

if not os.path.exists('/mnt/katib'):
    os.makedirs('/mnt/katib')

with ZipFile('katib_dataset.zip', 'r') as zipObj:
   zipObj.extractall('/mnt/katib')

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2 * ((precision * recall) / (precision + recall + K.epsilon()))

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('--batchsize',
                      type=int,
                      default=32,
                      help='The number of batch size during training')
    parser.add_argument('--beta1', type=float, default=0.1,
                        help='Initial beta1 rate')
    parser.add_argument('--beta2', type=float, default=0.5,
                        help='Initial beta2 rate')
    parser.add_argument('--learningrate',
                      type=float,
                      default=0.01,
                      help='Learning rate for training.')

    args, unparsed = parser.parse_known_args()
    return args

def main(unused_args):
    
    tf.logging.set_verbosity(tf.logging.INFO)
    args = parse_arguments()
    print("[INFO] loading images...")
    imagePaths = list(paths.list_images("/mnt/katib"))
    data = []
    labels = []

    if not os.path.exists('/mnt/Model_Covid'):
        os.makedirs('/mnt/Model_Covid')
    
    for imagePath in imagePaths:
        label = imagePath.split(os.path.sep)[-2]
        image = cv2.imread(imagePath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))
        data.append(image)
        labels.append(label)
   
    data = np.array(data) / 255.0
    labels = np.array(labels)
    lb = LabelBinarizer()
    labels = lb.fit_transform(labels)
    labels = to_categorical(labels)
    
    (trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=.2)
    print(trainX.shape,trainY.shape)

    # load the VGG16 network, ensuring the head FC layer sets are left off
    baseModel = VGG16(weights="imagenet", include_top=False,
                      input_tensor=Input(shape=(224, 224, 3)))
    # construct the head of the model that will be placed on top of the
    # the base model
    headModel = baseModel.output
    headModel = AveragePooling2D(pool_size=(4, 4))(headModel)
    headModel = Flatten(name="flatten")(headModel)
    headModel = Dense(64, activation="relu")(headModel)
    headModel = Dropout(0.5)(headModel)
    headModel = Dense(2, activation="softmax")(headModel)
    # place the head FC model on top of the base model (this will become
    # the actual model we will train)
    model = Model(inputs=baseModel.input, outputs=headModel)
    # loop over all layers in the base model and freeze them so they will
    # *not* be updated during the first training process
    for layer in baseModel.layers:
        layer.trainable = False

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    model.compile(loss='binary_crossentropy', optimizer=tf.train.AdamOptimizer(learning_rate=args.learningrate,beta1=args.beta1, beta2=args.beta2), metrics=['acc',f1_m,precision_m, recall_m])
    history = model.fit(trainX,trainY,batch_size=args.batchsize,epochs=5, validation_split=0.1)    
    evaluation = model.evaluate(testX,testY)
    loss = evaluation[0]
    accuracy = evaluation[1]
    
    print('accuracy='+str(accuracy))
    print('loss='+str(loss))  
    print('accuracy=',accuracy)
    print('loss=',loss) 

if __name__ == "__main__":
    tf.app.run()
