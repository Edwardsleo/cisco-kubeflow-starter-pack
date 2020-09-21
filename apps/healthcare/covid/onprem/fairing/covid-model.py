#Python script for creating & training COVID-forecast model

import pandas as pd
import numpy as np
import datetime
import os
import argparse


import tensorflow as tf
import keras

from keras.models import Model
from keras import layers
from keras import Input
from keras import optimizers

from datetime import timedelta


def preprocess_train(n_prev, n_next):
    df = train_df.copy()
    input_feats, output_feats = [], []
    
    # Performing Shifting of Previous cases in the positive direction (downwards) for New cases & New Fatalities
    for i in range(1, n_prev+1):
        for feat in ["NewCases", "NewFatalities"]:
            df["{}_prev_{}".format(feat, i)] = df.groupby(["Country_Region", "Province_State"])[feat].shift(i)
            input_feats.append("{}_prev_{}".format(feat, i))
    
    # Performing Shifting of Next Cases in the negative direction (upwards) for New cases & New Fatalities
    output_feats.extend(["NewCases", "NewFatalities"])
    for i in range(1, n_next):
        for feat in ["NewCases", "NewFatalities"]:
            df["{}_next_{}".format(feat, i)] = df.groupby(["Country_Region", "Province_State"])[feat].shift(-i)
            output_feats.append("{}_next_{}".format(feat, i))
    df.dropna(inplace=True)     
    
    #Converting the Province state & Country Region to Dummy/Indicator Variables ( which is a constant)
    const_df = pd.get_dummies(df[["Province_State", "Country_Region"]], drop_first=True)
    
    # Assigning already available data for previous no of days counting back from starting date of forecasting dates
    time_df = df[input_feats]
    time_df = time_df.values.reshape((df.shape[0],-1,2))
    
    #Assigning values to the future no of days counting forth from the starting date of forecasting dates
    output_df = df[output_feats]
    return const_df, time_df, output_df

def preprocess_test(n_prev):
    input_feats = []
    
    #Appending the training data with test data records with date of specified no of forecasting dates
    append_df = pd.concat([train_df, test_df[test_df["Date"] == train_df["Date"].max() + timedelta(days=1)]])
    
    #Sorting the Dataframe in ascending order of Country region, province state & Date
    append_df.sort_values(["Country_Region", "Province_State", "Date"], ascending=[True, True, True], inplace=True)
    
    # Performing Shifting of Previous cases in the positive direction (downwards) for New cases & New Fatalities
    for i in range(1, n_prev+1):
        for feat in ["NewCases", "NewFatalities"]:
            append_df["{}_prev_{}".format(feat, i)] = append_df.groupby(["Country_Region", "Province_State"])[feat].shift(i)
            input_feats.append("{}_prev_{}".format(feat, i))
            
    # Adding a column of ForecastId if records are not having null values        
    append_df = append_df[append_df["ForecastId"].notnull()]
    
    #Converting the Province state & Country Region to Dummy/Indicator Variables ( which is a constant)
    const_df = pd.get_dummies(append_df[["Province_State", "Country_Region"]], drop_first=True)
    
    # Assigning already available data for previous no of days counting back from starting date of forecasting dates
    time_df = append_df[input_feats]
    time_df = time_df.values.reshape((append_df.shape[0],-1,2))
    
    return const_df, time_df

if __name__== "__main__":
    
        parser = argparse.ArgumentParser()

        parser.add_argument('--batch-size',
                          type=int,
                          default=128,
                          help='The number of batch size during training')
        parser.add_argument('--optimizer',
                          type=str,
                          default='adam',
                          help='Type of optimizer used for training')
        parser.add_argument('--epochs',
                          type=int,
                          default=10,
                          help='The number of passed through entire training dataset')
        FLAGS, unparsed = parser.parse_known_args()



        # Read train and test datasets
        train_df = pd.read_csv("/opt/train.csv")
        print("train_df shape: {0}" .format(train_df.shape))
        test_df = pd.read_csv("/opt/test.csv")
        print("train_df shape: {0}" .format(test_df.shape))

        # Check the NaN value status in each column of the Train data
        # Checking whether no column except Province_State are having NaN values
        train_df.apply(lambda col: col.isnull().value_counts(), axis=0)
        test_df.apply(lambda col: col.isna().value_counts(), axis=0)

        # Replace the values of NaN with ""
        train_df["Province_State"] = train_df["Province_State"].fillna("")
        test_df["Province_State"] = test_df["Province_State"].fillna("")

        # Convert the Date column values to Pandas Datetime format
        train_df["Date"] = pd.to_datetime(train_df["Date"])
        test_df["Date"] = pd.to_datetime(test_df["Date"])

        # Add New Columns for "NewCases" and Fill the Column with difference values from the previous rows
        train_df["NewCases"] = train_df.groupby(["Country_Region", "Province_State"])["ConfirmedCases"].diff(periods=1)

        # Replace "NewCases" NaN values with 0
        train_df["NewCases"] = train_df["NewCases"].fillna(0)

        # Ensure that the NewCases are not negative. If NewCases are negative then they are replaced with zero else the actual value    is provided
        train_df["NewCases"] = np.where(train_df["NewCases"] < 0, 0, train_df["NewCases"])

        # Add a column for "NewFatalities" same as for "NewCases"
        train_df["NewFatalities"] = train_df.groupby(["Country_Region", "Province_State"])["Fatalities"].diff(periods=1)
        train_df["NewFatalities"] = train_df["NewFatalities"].fillna(0)
        train_df["NewFatalities"] = np.where(train_df["NewFatalities"] < 0, 0, train_df["NewFatalities"])

        # Apply Natural Logarithmic Function to NewCases and NewFatalities Column
        train_df["NewCases"] = np.log(train_df["NewCases"] + 1)
        train_df["NewFatalities"] = np.log(train_df["NewFatalities"] + 1)
        print("train_df \n", train_df.head())
        print("test_df \n", test_df.head())



        n_next = (test_df["Date"].max() - train_df["Date"].max()).days
        print("No of Future Days requested to forecast COVID-19 New Cases & New Fatalities:", n_next)

        const_df, time_df, output_df = preprocess_train(n_next, n_next)

        const_test_df, time_test_df = preprocess_test(n_next)

        time_input = Input(shape=(time_df.shape[1], time_df.shape[2]))
        lstm = layers.LSTM(64)(time_input)

        const_input = Input(shape=(const_df.shape[1],))

        combine = layers.concatenate([lstm, const_input], axis=-1)
        #lstm_out = layers.Dropout(0.1)(combine)
        output = layers.Dense(output_df.shape[1], activation='softmax')(combine)

        model = Model([time_input, const_input], output)
        #optimizer=optimizers.SGD(lr=0.01, nesterov=True)
        model.compile(optimizer=FLAGS.optimizer ,loss='mean_squared_error',metrics=['acc'])
        model.summary()

        model.fit([time_df, const_df], output_df, epochs=FLAGS.epochs, batch_size=FLAGS.batch_size)

        input_names = ['input1','input2']
        name_to_input = {name: t_input for name, t_input in zip(input_names, model.inputs)}
        MODEL_EXPORT_PATH='covid-model'

        tf.saved_model.simple_save(
            keras.backend.get_session(),
            os.path.join(MODEL_EXPORT_PATH, "001"),
            inputs=name_to_input,
            outputs={t.name: t for t in model.outputs})

        score = model.evaluate([time_df, const_df], output_df)
        print("Accuracy=%.2f%%" %(score[1]))




