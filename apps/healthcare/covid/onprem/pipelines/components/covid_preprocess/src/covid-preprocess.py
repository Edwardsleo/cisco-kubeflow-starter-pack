#Code for Preprocessing the COVID-19 data 

import pandas as pd
import numpy as np
import datetime


train_df = pd.read_csv("/opt/train.csv")
test_df = pd.read_csv("/opt/test.csv")

train_df.apply(lambda col: col.isnull().value_counts(), axis=0)
test_df.apply(lambda col: col.isna().value_counts(), axis=0)

train_df["Province_State"] = train_df["Province_State"].fillna("")
test_df["Province_State"] = test_df["Province_State"].fillna("")

train_df["Date"] = pd.to_datetime(train_df["Date"])
test_df["Date"] = pd.to_datetime(test_df["Date"])

train_df["NewCases"] = train_df.groupby(["Country_Region", "Province_State"])["ConfirmedCases"].diff(periods=1)
train_df["NewCases"] = train_df["NewCases"].fillna(0)
train_df["NewCases"] = np.where(train_df["NewCases"] < 0, 0, train_df["NewCases"])
train_df["NewFatalities"] = train_df.groupby(["Country_Region", "Province_State"])["Fatalities"].diff(periods=1)
train_df["NewFatalities"] = train_df["NewFatalities"].fillna(0)
train_df["NewFatalities"] = np.where(train_df["NewFatalities"] < 0, 0, train_df["NewFatalities"])

train_df["NewCases"] = np.log(train_df["NewCases"] + 1)
train_df["NewFatalities"] = np.log(train_df["NewFatalities"] + 1)

def preprocess_train(n_prev, n_next):
    df = train_df.copy()
    input_feats, output_feats = [], []
    for i in range(1, n_prev+1):
        for feat in ["NewCases", "NewFatalities"]:
            df["{}_prev_{}".format(feat, i)] = df.groupby(["Country_Region", "Province_State"])[feat].shift(i)
            input_feats.append("{}_prev_{}".format(feat, i))
    
    output_feats.extend(["NewCases", "NewFatalities"])
    for i in range(1, n_next):
        for feat in ["NewCases", "NewFatalities"]:
            df["{}_next_{}".format(feat, i)] = df.groupby(["Country_Region", "Province_State"])[feat].shift(-i)
            output_feats.append("{}_next_{}".format(feat, i))
    df.dropna(inplace=True)       
            
    const_df = pd.get_dummies(df[["Province_State", "Country_Region"]], drop_first=True)
    print("Adding dummies to the data frame")
    print(const_df)
    
    time_df = df[input_feats]
    time_df = time_df.values.reshape((df.shape[0],-1,2))
    print("Data Frame with input features")
    print(time_df)
    
    output_df = df[output_feats]
    print("Data Frame with output features")
    print(output_df)
    
    print("Saving the training data preprocess results in a CSV File....")      
    const_df.to_csv(r'/mnt/const_df.csv', index=False)
    np.save(r'/mnt/time_df.npy', time_df)
    output_df.to_csv(r'/mnt/output_df.csv', index=False)
    
    print("Training data Preprocess Results saved successfully in mounted volume")
    
    return const_df, time_df, output_df


def preprocess_test(n_prev):
    input_feats = []
    append_df = pd.concat([train_df, test_df[test_df["Date"] == train_df["Date"].max() + timedelta(days=1)]])
    append_df.sort_values(["Country_Region", "Province_State", "Date"], ascending=[True, True, True], inplace=True)
    for i in range(1, n_prev+1):
        for feat in ["NewCases", "NewFatalities"]:
            append_df["{}_prev_{}".format(feat, i)] = append_df.groupby(["Country_Region", "Province_State"])[feat].shift(i)
            input_feats.append("{}_prev_{}".format(feat, i))
    append_df = append_df[append_df["ForecastId"].notnull()]
            
    const_df = pd.get_dummies(append_df[["Province_State", "Country_Region"]], drop_first=True)
    print("Adding dummies to the data frame for test data")
    print(const_df)
    
    time_df = append_df[input_feats]
    time_df = time_df.values.reshape((append_df.shape[0],-1,2))
    print("Data Frame with input features for test data")
    print(time_df)
    
    print("Saving the testing data preprocess results in a CSV File....")
    const_df.to_csv(r'/mnt/const_test_df.csv', index=False)
    np.save(r'/mnt/time_test_df.npy', time_df)
    
    print("Testing data Preprocess Results saved successfully in mounted volume")
    
    return const_df, time_df

n_next = (test_df["Date"].max() - train_df["Date"].max()).days


from datetime import timedelta

#Invoking the preprocess functions
preprocess_train(n_next, n_next)
preprocess_test(n_next)

print("Preprocessing of data is complete")

#Writing the modified train and test data and saving thems
train_df.to_csv(r'/mnt/train_df.csv', index=False)
test_df.to_csv(r'/mnt/test_df.csv', index=False)



