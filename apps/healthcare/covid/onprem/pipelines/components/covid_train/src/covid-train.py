#Code for implementing creation and training of COVID-19 forecast model

import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import argparse

from keras.models import Model
from keras import layers
from keras import Input
from keras import optimizers

import tensorflow as tf
import keras

#Define and parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--epochs', 
                      type=int, default=100,
                      help='Number of epochs for training.')
parser.add_argument('--batch_size', 
                       type=int, default=64,
                      help='Training batch size')
args = parser.parse_args()

#Read the preprocess results from mounted volume
const_df = pd.read_csv(r'/mnt/const_df.csv')
time_df = np.load(r'/mnt/time_df.npy')
output_df = pd.read_csv(r'/mnt/output_df.csv')                      
const_test_df = pd.read_csv(r'/mnt/const_test_df.csv')
time_test_df = np.load(r'/mnt/time_test_df.npy')

#Create a tensor of input
time_input = Input(shape=(time_df.shape[1], time_df.shape[2]))

# Define Keras layers
lstm = layers.LSTM(64)(time_input)

const_input = Input(shape=(const_df.shape[1],))

combine = layers.concatenate([lstm, const_input], axis=-1)
#lstm_out = layers.Dropout(0.1)(combine)
output = layers.Dense(output_df.shape[1], activation='softmax')(combine)

#Create a Model
model = Model([time_input, const_input], output)
#optimizer=optimizers.SGD(lr=0.01, nesterov=True)
model.compile(optimizer='adam',loss='mean_squared_error',metrics=['acc'])
model.summary()

print("Training the Model...")

model.fit([time_df, const_df], output_df, epochs=args.epochs, batch_size=args.batch_size)

#Converting the model to TensorflowServing Servable format and saving it
input_names = ['input1','input2']
name_to_input = {name: t_input for name, t_input in zip(input_names, model.inputs)}

MODEL_EXPORT_PATH='/mnt/Model_Covid/1'

#Saving the model in .pb format
tf.saved_model.simple_save(
    keras.backend.get_session(),
    MODEL_EXPORT_PATH,
    inputs=name_to_input,
    outputs={t.name: t for t in model.outputs})

output = model.predict([time_test_df, const_test_df])
print("Output shape",output.shape)

#Read modified train and test data
train_df = pd.read_csv(r'/mnt/train_df.csv')
test_df = pd.read_csv(r'/mnt/test_df.csv')

sub_test_df = test_df[test_df["Date"] > train_df["Date"].max()]
sub_test_df = pd.concat([sub_test_df,
                         pd.DataFrame(output.reshape((-1, 2)), columns=["NewCases", "NewFatalities"], index=sub_test_df.index)],
                         axis=1)
sub_test_df["NewCases"] = np.exp(sub_test_df["NewCases"]) - 1
sub_test_df["NewFatalities"] = np.exp(sub_test_df["NewFatalities"]) - 1

fixed_test_df = test_df[test_df["Date"] <= train_df["Date"].max()].merge(train_df[train_df["Date"] >= test_df["Date"].min()][["Province_State","Country_Region", "Date", "ConfirmedCases", "Fatalities"]],
                                                                         how="left", on=["Province_State","Country_Region", "Date"])

predict_df = pd.concat([sub_test_df, fixed_test_df]).sort_values(["Country_Region", "Province_State", "Date"],
                                                                 ascending=[True, True, True])
predict_df = predict_df.reset_index()
for i in range(len(predict_df)):
    if pd.isnull(predict_df.iloc[i]["ConfirmedCases"]):
        predict_df.loc[i, "ConfirmedCases"] = predict_df.iloc[i - 1]["ConfirmedCases"] + predict_df.iloc[i]["NewCases"]
    if pd.isnull(predict_df.iloc[i]["Fatalities"]):
        predict_df.loc[i, "Fatalities"] = predict_df.iloc[i - 1]["Fatalities"] + predict_df.iloc[i]["NewFatalities"]
print("predict_df",predict_df)

assert predict_df.shape[0] == test_df.shape[0]

#Display predicted results
print(predict_df[["ForecastId", "ConfirmedCases", "Fatalities"]].head())

#Write predicted results to mounted volume
predict_df.to_csv(r'/mnt/predict_df.csv', index=False)



