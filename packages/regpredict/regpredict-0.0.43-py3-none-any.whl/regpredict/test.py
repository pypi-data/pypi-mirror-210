import pandas as pd
from regbot import signal

df = pd.read_csv('../reinforce/regbot_v43_training.csv')

y_pred = []
def getSignal(v,w,x,y,z):
    #return signal(v,w,x,y,z)
    return signal(v,w,x,y,z)

print(df.head())
df = df.sample(frac=1).reset_index(drop=True)
print(df.head())
df = df[df['targets'] == -1].tail(20)
print(df.head())

df['result'] = df.apply(lambda row: getSignal(row['rsi-05'],row['rsi-15'],row['close-gradient'], row['close-gradient-neg'], row['grad-sma-25']), axis=1)

print(df.head())

print(len(df[df['result'] == df['targets']]), len(df))
