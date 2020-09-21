import tensorflow as tf
import pandas as pd
import numpy as np
import tempfile
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,MinMaxScaler
from sklearn.model_selection import KFold
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import RandomOverSampler
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

import shutil
import argparse

'''Coloumns contains 0'''
lstZerodrp=['Timestamp','BwdPSHFlags','FwdURGFlags','BwdURGFlags','CWEFlagCount','FwdBytsbAvg','FwdPktsbAvg','FwdBlkRateAvg','BwdBytsbAvg',
 'BwdBlkRateAvg','BwdPktsbAvg']

'''Coloumns contains 1'''
lstScaledrp=['FwdPSHFlags','FINFlagCnt','SYNFlagCnt','RSTFlagCnt','PSHFlagCnt','ACKFlagCnt','URGFlagCnt','ECEFlagCnt']

DATA_FILE =  '/opt/Network_Traffic.csv'

'''Dataset preprocess'''
def read_dataFile():
    chunksize = 10000
    chunk_list = []
    missing_values = ["n/a", "na", "--", "Infinity", "infinity", "Nan", "NaN"]

    for chunk in pd.read_csv(DATA_FILE, chunksize=chunksize, na_values = missing_values):
        chunk_list.append(chunk)
        break
    dataFrme = pd.concat(chunk_list)

    lstcols = []
    for i in dataFrme.columns:
        i = str(i).replace(' ','').replace('/','')
        lstcols.append(i)
    dataFrme.columns=lstcols
    dfAllCpy = dataFrme.copy()
    dataFrme = dataFrme.drop(lstZerodrp,axis=1)
    return dataFrme

'''Remove NA'''
def preprocess_na(dataFrme):
    na_lst = dataFrme.columns[dataFrme.isna().any()].tolist()
    for j in na_lst:
        dataFrme[j].fillna(0, inplace=True)
    return dataFrme


def create_features_label(dataFrme):
    #Create independent and Dependent Features
    columns = dataFrme.columns.tolist()
    # Filter the columns to remove data we do not want 
    columns = [c for c in columns if c not in ["Label"]]
    # Store the variable we are predicting 
    target = "Label"
    # Define a random state 
    state = np.random.RandomState(42)
    X = dataFrme[columns]
    Y = dataFrme[target]
    return X,Y

'''Label substitution'''
def label_substitution(dataFrme):
    dictLabel = {'Benign':0,'Bot':1}
    dataFrme['Label']= dataFrme['Label'].map(dictLabel)
    
    LABELS=['Benign','Bot']
    count_classes = pd.value_counts(dataFrme['Label'], sort = True)
    print(count_classes)
    
    # Get the Benign and the Bot values 
    Benign = dataFrme[dataFrme['Label']==0]
    Bot = dataFrme[dataFrme['Label']==1]
    return dataFrme

'''Class Imabalancement'''
def handle_class_imbalance(X,Y):
#    os_us = SMOTETomek(ratio=0.5)
#    X_res, y_res = os_us.fit_sample(X, Y)
    ros = RandomOverSampler(random_state=50)
    X_res, y_res = ros.fit_sample(X, Y)
    ibtrain_X = pd.DataFrame(X_res,columns=X.columns)
    ibtrain_y = pd.DataFrame(y_res,columns=['Label']) 
    return ibtrain_X,ibtrain_y

'''Feature Selection'''
def correlation_features(ibtrain_X):
    # Correlation Ananlysis
    corr = ibtrain_X.corr()
    cor_columns = np.full((corr.shape[0],), True, dtype=bool)
    for i in range(corr.shape[0]):
        for j in range(i+1, corr.shape[0]):
            if corr.iloc[i,j] >= 0.9:
                if cor_columns[j]:
                    cor_columns[j] = False
                    
    dfcorr_features = ibtrain_X[corr.columns[cor_columns]]
    return dfcorr_features

''' Highly Coorelated features '''
def top_ten_features(dfcorr_features,ibtrain_X,ibtrain_y):
    feat_X = dfcorr_features
    feat_y = ibtrain_y['Label']
    
    #apply SelectKBest class to extract top 10 best features
    bestfeatures = SelectKBest(score_func=f_classif, k=10)
    fit = bestfeatures.fit(feat_X,feat_y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(feat_X.columns)
    #concat two dataframes for better visualization 
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Features','Score']  #naming the dataframe columns
    final_feature = featureScores.nlargest(10,'Score')['Features'].tolist()
    print(type(final_feature))
    final_feature.sort()
    sort_fn = final_feature
    print('*******************')
    print(sort_fn)
    dictLabel1 = {'Benign':0,'Bot':1}
    ibtrain_y['Label']= ibtrain_y['Label'].map(dictLabel1)
    selected_X = ibtrain_X[sort_fn]
    selected_Y = ibtrain_y['Label']
    return selected_X,selected_Y,sort_fn

'''Scaling'''
def normalize_data(selected_X,selected_Y):
    scaler = MinMaxScaler(feature_range=(0, 1))
    selected_X = pd.DataFrame(scaler.fit_transform(selected_X),columns=selected_X.columns, index=selected_X.index)
    trainX, testX, trainY, testY= train_test_split(selected_X,selected_Y, test_size=0.25)
    return trainX, testX, trainY, testY

def prec_metric(labels, predictions):
    predicted_classes = predictions["class_ids"]  
    prec_metric = tf.metrics.precision(labels, predicted_classes, name="prec_metric")
    return {"prec_metric": prec_metric}

def recall_metric(labels, predictions):
    predicted_classes = predictions["class_ids"]  
    recall_metric = tf.metrics.recall(labels, predicted_classes, name="recall_metric")
    return {"recall_metric": recall_metric}

def f1_metric(labels, predictions):
    predicted_classes = predictions["class_ids"]  
    f1_score = tf.contrib.metrics.f1_score(labels, predicted_classes, name="f1_score")
    return {"f1_score": f1_score}

def predict_input_fn(testX):
      return tf.estimator.inputs.pandas_input_fn(
      x=testX,
      num_epochs=1,
      shuffle=False
      )


def get_model(trainX,trainY,testX,testY,final_feature,args):
    
    TF_MODEL_DIR = '/mnt/Model_Network/'
    TF_EXPORT_DIR1='/mnt/Model_Network/'
    print('****************Get the featture list*')
    print(final_feature)
    print('*****************************************')
    input_columns = [tf.feature_column.numeric_column(k) for k in final_feature]
    feature_spec = tf.feature_column.make_parse_example_spec(input_columns)
    serving_input_receiver_fn = tf.estimator.export.build_parsing_serving_input_receiver_fn(feature_spec)
    seed = 1000
    config = tf.estimator.RunConfig(model_dir=TF_MODEL_DIR, save_summary_steps=100, save_checkpoints_steps=1000, tf_random_seed=seed)

    train_input_fn = tf.estimator.inputs.pandas_input_fn(
        x = trainX,
        y = trainY,
        batch_size = 64,
        num_epochs = 1000,
        shuffle = False,
        queue_capacity = 100,
        num_threads = 1
    )
    test_input_fn = tf.estimator.inputs.pandas_input_fn(
        x = testX,
        y = testY,
        batch_size = 64,
        num_epochs = 10,
        shuffle = True,
        queue_capacity = 10,
        num_threads = 1
    )
    
    model =tf.estimator.DNNClassifier(feature_columns=input_columns,
                                        hidden_units=[32, 64, 128],
                                        n_classes=2,activation_fn=tf.nn.relu,dropout=0.2,batch_norm=False)
    
    # Adding your custom metrics:
    model = tf.contrib.estimator.add_metrics(model, prec_metric)
    model = tf.contrib.estimator.add_metrics(model, recall_metric)
    model = tf.contrib.estimator.add_metrics(model, f1_metric)
    
    export_final = tf.estimator.FinalExporter(TF_EXPORT_DIR1, serving_input_receiver_fn=serving_input_receiver_fn)

    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, 
                                    max_steps=1200)

    eval_spec = tf.estimator.EvalSpec(input_fn=test_input_fn,
                                  steps=1200,
                                  exporters=export_final,
                                  throttle_secs=2,
                                  start_delay_secs=2)
                                      
    result = tf.estimator.train_and_evaluate(model, train_spec, eval_spec)
    print(result)

    predictions = model.predict(input_fn=predict_input_fn(testX))
    pred_list = list(predictions)
    predicted_output = [int(predictions['classes']) for predictions in pred_list]
    
    from sklearn.metrics import classification_report,confusion_matrix
    print('Confusion Matrx')
    cm = confusion_matrix(testY, predicted_output)
    total = sum(sum(cm))
    acc = (cm[0, 0] + cm[1, 1]) / total
    sensitivity = cm[0, 0] / (cm[0, 0] + cm[0, 1])
    specificity = cm[1, 1] / (cm[1, 0] + cm[1, 1])
    print(cm)
    print("acc: {:.4f}".format(acc))
    print("sensitivity: {:.4f}".format(sensitivity))
    print("specificity: {:.4f}".format(specificity))
    
    print('Classification Report')
    print(classification_report(testY, predicted_output))
    
    import pandas as pd
    df1 = pd.DataFrame({'actual': testY,'pred': predicted_output})
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('/mnt/network_source.xlsx', engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    # df2 = df1+df
    df1.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    with open('/tf_export_dir.txt', 'w') as f:
      f.write(args.tf_export_dir)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tf-model-dir',
                      type=str,
                      help='GCS path or local directory.')
    parser.add_argument('--tf-export-dir',
                      type=str,
                      default='rssi/',
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
    parser.add_argument('--tf-learning-rate',
                      type=float,
                      default=0.01,
                      help='Learning rate for training.')

    args = parser.parse_args()
    return args


def main(unused_args):

    args = parse_arguments()

    tf.logging.set_verbosity(tf.logging.INFO)
    
    '''functionalities'''
    dataFrme = read_dataFile()
#     print(dataFrme.shape)

    dataFrme = preprocess_na(dataFrme)
#     print(dataFrme.isnull().values.any())

    X,Y = create_features_label(dataFrme)
    print(X.shape,Y.shape)
    
    dataFrme = label_substitution(dataFrme)
#     print(dataFrme.shape)

    ibtrain_X,ibtrain_y = handle_class_imbalance(X,Y)
    print(ibtrain_X.shape,ibtrain_y.shape)
    
    dfcorr_features = correlation_features(ibtrain_X)
    print(dfcorr_features.shape)
    
    selected_X,selected_Y,final_feature = top_ten_features(dfcorr_features,ibtrain_X,ibtrain_y)
    print(selected_X.shape,selected_Y.shape)
    
    trainX, testX, trainY, testY = normalize_data(selected_X,selected_Y)
    print(trainX.shape, testX.shape, trainY.shape, testY.shape)
    
    get_model(trainX,trainY,testX,testY,final_feature,args)
    
    print('Training finished successfully')

if __name__ == "__main__":
    tf.app.run()
