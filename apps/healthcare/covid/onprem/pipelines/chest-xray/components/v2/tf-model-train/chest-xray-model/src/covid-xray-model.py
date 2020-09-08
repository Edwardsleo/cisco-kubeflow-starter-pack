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

import pandas as pd
from tensorflow.keras import backend as K
from tensorflow.keras.utils import multi_gpu_model
import tensorflow as tf
tf.keras.backend.set_learning_phase(0)

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

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
    parser.add_argument('--epochs',
                        type=int,
                        default=25,
                        help='The number of times repeat during training')
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
    parser.add_argument('--timestamp',
                      type=str,
                      help='Timestamp value')
    args, unparsed = parser.parse_known_args()
    return args

def main(unused_args):
    
    tf.logging.set_verbosity(tf.logging.INFO)
    args = parse_arguments()
    
    timestamp = str(args.timestamp)
    filename = "/mnt/Model_Covid/hpv-"+timestamp+".txt"
    f = open(filename, "r")
    batchsize = int(f.readline())
    learningrate = float(f.readline())
    print("[INFO] loading images...")
    imagePaths = list(paths.list_images("/mnt/dataset"))
    data = []
    labels = []

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

    num_gpu = len(tf.config.experimental.list_physical_devices('GPU'))
    parallel_model = multi_gpu_model(model, gpus=num_gpu)
    parallel_model.compile(loss='binary_crossentropy', optimizer=tf.train.AdamOptimizer(learning_rate=learningrate), metrics=['acc',f1_m,precision_m, recall_m])
    
    history=parallel_model.fit(trainX,trainY,batch_size=batchsize,epochs=5, validation_split=0.1)
    print ("Katib learning rate : {} ||||  Batchsize :  {}".format(str(learningrate), str(batchsize))) 
    # make predictions on the testing set
    print("[INFO] evaluating network...")
    predIdxs = parallel_model.predict(testX, batch_size=args.batchsize)
    # for each image in the testing set we need to find the index of the
    # label with corresponding largest predicted probability
    predIdxs = np.argmax(predIdxs, axis=1)
    # show a nicely formatted classification report
    print(classification_report(testY.argmax(axis=1), predIdxs, target_names=lb.classes_))
    # compute the confusion matrix and and use it to derive the raw
    # accuracy, sensitivity, and specificity
    cm = confusion_matrix(testY.argmax(axis=1), predIdxs)
    total = sum(sum(cm))
    acc = (cm[0, 0] + cm[1, 1]) / total
    sensitivity = cm[0, 0] / (cm[0, 0] + cm[0, 1])
    specificity = cm[1, 1] / (cm[1, 0] + cm[1, 1])
    # show the confusion matrix, accuracy, sensitivity, and specificity
    print("acc: {:.4f}, sensitivity: {:.4f}, specificity: {:.4f}".format(acc,sensitivity,specificity))

    '''Model save - tensorflow pb format'''
    inputs = {"image": t for t in parallel_model.inputs}
    outputs = {t.name: t for t in parallel_model.outputs}    
    MODEL_EXPORT_PATH = '/mnt/Model_Covid/models/'
    
    dirFiles = os.listdir(MODEL_EXPORT_PATH) 
    modelno = 1
    if len(dirFiles) >=0:
        for i in dirFiles:
            if i == '.ipynb_checkpoints':
                dirFiles.remove(i)
                dirFiles.append(0)
                test_list = [int(i) for i in dirFiles]
                modelno = max(test_list) + 1
            else:
                test_list = [int(i) for i in dirFiles]
                modelno = max(test_list) + 1
    else:
        modelno = 1

    tf.saved_model.simple_save(
        tf.keras.backend.get_session(),
        os.path.join(MODEL_EXPORT_PATH, str(modelno)),
        inputs=inputs,
        outputs={t.name: t for t in parallel_model.outputs})

    print(os.path.join(MODEL_EXPORT_PATH, str(modelno)))

    '''Writing values to Visualization'''
    df1 = pd.DataFrame({'actual': testY.argmax(axis=1), 'pred': predIdxs})
    df = pd.DataFrame({'loss': history.history['loss'],
                       'val_loss': history.history['val_loss'], 'acc': history.history['acc'],
                       'val_acc': history.history['val_acc'],
                       'f1_m': history.history['f1_m'], 'val_f1_m': history.history['val_f1_m'],
                       'precision_m': history.history['precision_m'],
                       'val_precision_m': history.history['val_precision_m']})

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('/mnt/xray_source.xlsx', engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    # df2 = df1+df
    df1.to_excel(writer, sheet_name='Sheet1')
    df.to_excel(writer, sheet_name='Sheet2')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == "__main__":
    tf.app.run()
