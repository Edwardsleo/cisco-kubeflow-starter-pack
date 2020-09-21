from __future__ import division
from __future__ import print_function

import tensorflow as tf
import pandas as pd
import numpy as np
import argparse
import re
import os
import dill
import logging
from alibi.explainers import AnchorTabular

tf.logging.set_verbosity(tf.logging.INFO)
BLE_RSSI = pd.read_csv('/opt/iBeacon_RSSI_Labeled.csv') #Labeled dataset

# Configure model options
TF_DATA_DIR = os.getenv("TF_DATA_DIR", "/tmp/data/")
TF_MODEL_DIR = os.getenv("TF_MODEL_DIR", "blerssi/")
TF_EXPORT_DIR = os.getenv("TF_EXPORT_DIR", "blerssi/")
TF_MODEL_TYPE = os.getenv("TF_MODEL_TYPE", "DNN")
TF_TRAIN_STEPS = int(os.getenv("TF_TRAIN_STEPS", 5000))
TF_BATCH_SIZE = int(os.getenv("TF_BATCH_SIZE", 128))
TF_LEARNING_RATE = float(os.getenv("TF_LEARNING_RATE", 0.001))


# Feature columns
COLUMNS = list(BLE_RSSI.columns)
FEATURES = COLUMNS[2:]
def make_feature_cols():
  input_columns = [tf.feature_column.numeric_column(k) for k in FEATURES]
  return input_columns

feature_columns =  make_feature_cols()
inputs = {}
for feat in feature_columns:
  inputs[feat.name] = tf.placeholder(shape=[None], dtype=feat.dtype)
serving_input_receiver_fn = tf.estimator.export.build_raw_serving_input_receiver_fn(inputs)

def main(unused_args):

    ##Read hypertuning values from file
    if args.component=='training':
        timestamp = str(args.timestamp)

        filename = "/mnt/Model_Blerssi/hpv-"+timestamp+".txt"
        f = open(filename, "r")
        args.tf_batch_size = int(f.readline())
        args.learning_rate = float(f.readline())
        print("****************")
        print("Optimized Hyper paramater value")
        print("Batch-size = " + str(args.tf_batch_size))
        print("Learning rate = "+ str(args.learning_rate))
        print("****************")

    # Feature columns
    COLUMNS = list(BLE_RSSI.columns)
    FEATURES = COLUMNS[2:]
    LABEL = [COLUMNS[0]]

    b3001 = tf.feature_column.numeric_column(key='b3001',dtype=tf.float64)
    b3002 = tf.feature_column.numeric_column(key='b3002',dtype=tf.float64)
    b3003 = tf.feature_column.numeric_column(key='b3003',dtype=tf.float64)
    b3004 = tf.feature_column.numeric_column(key='b3004',dtype=tf.float64)
    b3005 = tf.feature_column.numeric_column(key='b3005',dtype=tf.float64)
    b3006 = tf.feature_column.numeric_column(key='b3006',dtype=tf.float64)
    b3007 = tf.feature_column.numeric_column(key='b3007',dtype=tf.float64)
    b3008 = tf.feature_column.numeric_column(key='b3008',dtype=tf.float64)
    b3009 = tf.feature_column.numeric_column(key='b3009',dtype=tf.float64)
    b3010 = tf.feature_column.numeric_column(key='b3010',dtype=tf.float64)
    b3011 = tf.feature_column.numeric_column(key='b3011',dtype=tf.float64)
    b3012 = tf.feature_column.numeric_column(key='b3012',dtype=tf.float64)
    b3013 = tf.feature_column.numeric_column(key='b3013',dtype=tf.float64)
    feature_columns = [b3001, b3002, b3003, b3004, b3005, b3006, b3007, b3008, b3009, b3010, b3011, b3012, b3013]

    df_full = pd.read_csv("/opt/iBeacon_RSSI_Labeled.csv") #Labeled dataset

    # Input Data Preprocessing 
    df_full = df_full.drop(['date'],axis = 1)
    df_full[FEATURES] = (df_full[FEATURES])/(-200)


    #Output Data Preprocessing
    dict = {'O02': 0,'P01': 1,'P02': 2,'R01': 3,'R02': 4,'S01': 5,'S02': 6,'T01': 7,'U02': 8,'U01': 9,'J03': 10,'K03': 11,'L03': 12,'M03': 13,'N03': 14,'O03': 15,'P03': 16,'Q03': 17,'R03': 18,'S03': 19,'T03': 20,'U03': 21,'U04': 22,'T04': 23,'S04': 24,'R04': 25,'Q04': 26,'P04': 27,'O04': 28,'N04': 29,'M04': 30,'L04': 31,'K04': 32,'J04': 33,'I04': 34,'I05': 35,'J05': 36,'K05': 37,'L05': 38,'M05': 39,'N05': 40,'O05': 41,'P05': 42,'Q05': 43,'R05': 44,'S05': 45,'T05': 46,'U05': 47,'S06': 48,'R06': 49,'Q06': 50,'P06': 51,'O06': 52,'N06': 53,'M06': 54,'L06': 55,'K06': 56,'J06': 57,'I06': 58,'F08': 59,'J02': 60,'J07': 61,'I07': 62,'I10': 63,'J10': 64,'D15': 65,'E15': 66,'G15': 67,'J15': 68,'L15': 69,'R15': 70,'T15': 71,'W15': 72,'I08': 73,'I03': 74,'J08': 75,'I01': 76,'I02': 77,'J01': 78,'K01': 79,'K02': 80,'L01': 81,'L02': 82,'M01': 83,'M02': 84,'N01': 85,'N02': 86,'O01': 87,'I09': 88,'D14': 89,'D13': 90,'K07': 91,'K08': 92,'N15': 93,'P15': 94,'I15': 95,'S15': 96,'U15': 97,'V15': 98,'S07': 99,'S08': 100,'L09': 101,'L08': 102,'Q02': 103,'Q01': 104}
    df_full['location'] = df_full['location'].map(dict)
    df_train=df_full.sample(frac=0.8,random_state=200)
    df_valid=df_full.drop(df_train.index)
  
    location_counts = BLE_RSSI.location.value_counts()
    x1 = np.asarray(df_train[FEATURES])
    y1 = np.asarray(df_train['location'])

    x2 = np.asarray(df_valid[FEATURES])
    y2 = np.asarray(df_valid['location'])

    def formatFeatures(features):
        formattedFeatures = {}
        numColumns = features.shape[1]

        for i in range(0, numColumns):
            formattedFeatures["b"+str(3001+i)] = features[:, i]

        return formattedFeatures

    trainingFeatures = formatFeatures(x1)
    trainingCategories = y1

    testFeatures = formatFeatures(x2)
    testCategories = y2

    # Train Input Function
    def train_input_fn():
        dataset = tf.data.Dataset.from_tensor_slices((trainingFeatures, y1))
        dataset = dataset.repeat(args.epochs).batch(args.tf_batch_size)
        return dataset

    # Test Input Function
    def eval_input_fn():
        dataset = tf.data.Dataset.from_tensor_slices((testFeatures, y2))
        return dataset.repeat(args.epochs).batch(args.tf_batch_size)

    # Provide list of GPUs should be used to train the model

    distribution=tf.distribute.experimental.ParameterServerStrategy()
    print('Number of devices: {}'.format(distribution.num_replicas_in_sync))

    # Configuration of  training model

    config = tf.estimator.RunConfig(train_distribute=distribution, model_dir=args.tf_model_dir, save_summary_steps=100, save_checkpoints_steps=100)

    # Build 3 layer DNN classifier

    model = tf.estimator.DNNClassifier(hidden_units = [13,65,110],
                 feature_columns = feature_columns,
                 optimizer=tf.train.AdamOptimizer(learning_rate=args.learning_rate, beta1=args.beta1, beta2=args.beta2),
                 model_dir = args.tf_model_dir,
                 n_classes=105, config=config
               )

    export_final = tf.estimator.FinalExporter(args.tf_export_dir, serving_input_receiver_fn=serving_input_receiver_fn)

    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=args.tf_train_steps)

    eval_spec = tf.estimator.EvalSpec(input_fn=eval_input_fn, steps=100, exporters=export_final,  throttle_secs=1,  start_delay_secs=1)

    # Train and Evaluate the model

    tf.estimator.train_and_evaluate(model, train_spec, eval_spec)

    MODEL_EXPORT_PATH= args.tf_model_dir

    def predict(request):
        """ 
        Define custom predict function to be used by local prediction
        and explainer. Set anchor_tabular predict function so it always returns predicted class
        """
        # Get model exporter path
        for dir in os.listdir(args.tf_model_dir):
            if re.match('[0-9]',dir):
                exported_path=os.path.join(args.tf_model_dir,dir)
                break
        else:
            raise Exception("Model path not found")

        # Prepare model input data
        feature_cols=["b3001", "b3002","b3003","b3004","b3005","b3006","b3007","b3008","b3009","b3010","b3011","b3012","b3013"]
        input={'b3001': [], 'b3002': [], 'b3003': [], 'b3004': [], 'b3005': [], 'b3006': [], 'b3007': [], 'b3008': [], 'b3009': [], 'b3010': [], 'b3011': [], 'b3012': [], 'b3013': []}

        X=request
        if np.ndim(X) != 2:
            for i in range(len(X)):
                input[feature_cols[i]].append(X[i])
        else:
            for i in range(len(X)):
                for j in range(len(X[i])):
                    input[feature_cols[j]].append(X[i][j])

        # Open a Session to predict
        with tf.Session() as sess:
            tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], exported_path)
            predictor= tf.contrib.predictor.from_saved_model(exported_path,signature_def_key='predict')
            output_dict= predictor(input)
        sess.close()
        output={}
        output["predictions"]={"probabilities":output_dict["probabilities"].tolist()}
        return np.asarray(output['predictions']["probabilities"])

    #Initialize and fit
    feature_cols=["b3001", "b3002", "b3003", "b3004", "b3005", "b3006", "b3007", "b3008", "b3009", "b3010", "b3011", "b3012", "b3013"]
    explainer = AnchorTabular(predict, feature_cols)

    explainer.fit(x1, disc_perc=(25, 50, 75))

    #Save Explainer file
    #Save explainer file with .dill extension. It will be used when creating the InferenceService
    if not os.path.exists(args.explainer_dir):
        os.mkdir(args.explainer_dir)
    with open("%s/explainer.dill"%args.explainer_dir, 'wb') as f:
        dill.dump(explainer,f)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--tf-model-dir',
                      type=str,
                      default='/mnt/Model_Blerssi',
                      help='GCS path or local directory.')
    parser.add_argument('--tf-export-dir',
                      type=str,
                      default='/mnt/Model_Blerssi',
                      help='GCS path or local directory to export model')
    parser.add_argument('--tf-model-type',
                      type=str,
                      default='DNN',
                      help='Tensorflow model type for training.')
    parser.add_argument('--tf-train-steps',
                      type=int,
                      default=10000,
                      help='The number of training steps to perform.')
    parser.add_argument('--tf-batch-size',
                      type=int,
                      default=100,
                      help='The number of batch size during training')
    parser.add_argument('--learning-rate',
                      type=float,
                      default=0.01,
                      help='Learning rate for training.')
    parser.add_argument('--explainer-dir',
                      type=str,
                      default="/mnt/Model_Blerssi/explainer",
                      help='GCS path or local directory to save explainer file')
    parser.add_argument('--epochs',
                      type=int,
                      default=1000,
                      help='The number of times repeat during training')
    parser.add_argument('--beta1', type=float, default=0.1,
                      help='Initial learning rate')
    parser.add_argument('--beta2', type=float, default=0.5,
                        help='Initial learning rate')
    parser.add_argument('--timestamp',
                      type=str,
                      help='Timestamp value')
    parser.add_argument('--component',
                      type=str,
                      default="",
                      help='In which component you are running')
    args, unparsed = parser.parse_known_args()
    tf.app.run()
