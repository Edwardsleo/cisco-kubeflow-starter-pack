# Python script to visualise the predicted number of cases in India

import matplotlib.pyplot as plt
from pandas import read_csv

train_df = read_csv(source + '/train_df.csv')
predict_df = read_csv(source + '/predict_df.csv')

country = "India"

target = "ConfirmedCases"
region_train_df = train_df[(train_df["Country_Region"]==country)]
region_predict_df = predict_df[(predict_df["Country_Region"]==country)]

fig = plt.figure(figsize=(10,6))
ax1 = fig.add_axes([0,0,1,1])

ax1.plot(region_train_df["Date"],
         region_train_df[target],
         color="green")

         
ax1.plot(region_predict_df["Date"],
         region_predict_df[target],
         color="red")
         
plt.xticks(rotation=90)
plt.show()