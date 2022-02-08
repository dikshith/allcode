import pandas as pd
import numpy as np

#Create a Dictionary of series
d = {
     'Name':pd.Series(['Tom','James','Ricky','Vin','Steve','Smith','Jack']),
     'Age':pd.Series([25,26,25,23,30,29,23]),
     'Rating':pd.Series([4.23,3.24,3.98,2.56,3.20,4.6,3.8])
    }

#Create a DataFrame
df = pd.DataFrame(d)

print("Our data frame is:")
print(df)
print("*****************************************")
print("The first two rows of the data frame is:")
print(df.head(2))

print("*****************************************")
print("The last two rows of the data frame is:")
print(df.tail(2))