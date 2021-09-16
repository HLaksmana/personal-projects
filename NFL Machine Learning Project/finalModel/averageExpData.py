import pandas as pd 
import numpy as np

# Read data from file 'modellayerexp3.csv' 
# (in the same directory that your python process is based)
# Control delimiters, rows, column names with read_csv (see later) 
df = pd.read_csv(r"finalModel\NodeExpData.csv") 

df.columns=['x', 'LSTM_layers', 'Dense_layers', 'LSTMNodes', 'DenseNodes', 'MSE']

# res = (df.groupby(( (df.LSTMNodes != df.LSTMNodes.shift()) & (df.DenseNodes != df.DenseNodes.shift()) ).cumsum()).mean().reset_index(drop=True))
avg = 0
results = []
for rows in df.itertuples():
    if(rows.x < 6):
        avg += rows.MSE
    else:
       avg += rows.MSE
       avg /= 6
       results.append([rows.LSTMNodes, rows.DenseNodes, avg])
       avg = 0

np.savetxt("modellayerexp4.csv", results, delimiter=",")     