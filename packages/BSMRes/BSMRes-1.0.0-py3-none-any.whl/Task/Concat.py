import pandas as pd

df1 = pd.read_fwf("D:/MRes Data/EEG Data/One Line.csv")#, error_bad_lines=False)


df4 = pd.read_fwf("D:/MRes Data/EEG Data/One Line2.csv")
print(df4)
result = pd.concat([df1, df4], axis=1, join="inner")


print (result)
result.to_csv("D:/MRes Data/EEG Data/Output Trial Merge.csv", mode = 'a+', sep = '\t', header=False, index=False)

