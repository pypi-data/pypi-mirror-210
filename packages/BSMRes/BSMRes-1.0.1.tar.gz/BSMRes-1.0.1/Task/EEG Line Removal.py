import pandas as pd

for i in range(1,50):


    dfL = pd.read_fwf('MRes Data/EEG Data/' + str(i) + ' - L.txt',header=None)
    #print(dfL)

    dfLchanged = dfL.drop(labels=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,54,55,56,57,58,59,60])
    print(dfLchanged)
    dfLchanged.to_csv('MRes Data/EEG Data/' + str(i) + ' - L.csv', header = None, index=False, sep='\t')

    dfH = pd.read_fwf('MRes Data/EEG Data/' + str(i) + ' - H.txt',header=None)
    #print(dfL)

    dfHchanged = dfH.drop(labels=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,54,55,56,57,58,59,60])
    #print(dfHchanged)
    dfHchanged.to_csv('MRes Data/EEG Data/' + str(i) + ' - H.csv', header = None, index=False, sep='\t')






'''for i in range(1,50):
    df = pd.read_fwf('\MRes Data\EEG Data\Coherence/1 - L.csv')
    print (df)
    del df[df.columns[-1]]
    print (df)

'''


