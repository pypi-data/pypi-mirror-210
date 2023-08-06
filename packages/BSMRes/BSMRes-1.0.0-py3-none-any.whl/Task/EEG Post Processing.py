import pandas as pd
import numpy as np


widths = [100000000]

for i in range(1,36):
    
    df = pd.read_csv('MRes Data/EEG Data/' + str(i) + ' - L.csv', header=None)
    
    dfH = pd.read_csv('MRes Data/EEG Data/' + str(i) + ' - H.csv', header=None)

    df2 = df.apply(lambda x: x.astype(str).str.cat(sep=' '))

    print (df2)
    
    dfH2 = dfH.apply(lambda x: x.astype(str).str.cat(sep=' '))

    df2.to_csv("/MRes Data/EEG Data/One Line.csv", mode = "a+", index=False, sep='\t')

    dfH2.to_csv("/MRes Data/EEG Data/One Line2.csv", mode = "a+", index=False, sep='\t')

    ##########################################################################
    
    df1 = pd.read_fwf("/MRes Data/EEG Data/One Line.csv", sep='\t')


    df4 = pd.read_fwf("/MRes Data/EEG Data/One Line2.csv", sep='\t')
    

    result = pd.concat([df1, df4], axis=1, join="inner")

    print(str(i))
    print (result)

    result.to_csv("/MRes Data/EEG Data/Output EEG Data.csv", index=False)

df = pd.read_csv('D:/MRes Data/EEG Data/Output EEG Data.csv')
df = df.applymap(lambda x: x if '.' in str(x) else np.nan)
df = df.dropna(axis=1, how='all')
df = df.dropna(axis=0, how='any')

df.to_csv('D:/MRes Data/EEG Data/EEG Power Output.csv', index=False)


