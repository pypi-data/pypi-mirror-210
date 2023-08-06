import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# Load the two coherence matrices from separate CSV files
path1='MRes Data/EEG Data/Coherence/Processed Coherence/Theta H Coherence.csv'
path2='MRes Data/EEG Data/Coherence/Processed Coherence/Theta L Coherence.csv'


# Load the two coherence matrices from separate CSV files
coherence_df1 = pd.read_csv(path1, index_col=0)
coherence_df2 = pd.read_csv(path2, index_col=0)

# Calculate the difference between the two coherence matrices
diff_df = coherence_df2 - coherence_df1

# Calculate the p-values for each element using a two-sample t-test
p_values = np.zeros_like(diff_df.values)
for i in range(diff_df.shape[0]):
    for j in range(diff_df.shape[1]):
        group1 = coherence_df1.iloc[i,:]
        group2 = coherence_df2.iloc[j,:]
        t_stat, p_value = ttest_ind(group1, group2)
        p_values[i,j] = p_value

# Export p-values to CSV file
pd.DataFrame(p_values, index=coherence_df1.index, columns=coherence_df2.index).to_csv('MRes Data/EEG Data/Coherence/Processed Coherence/Theta Significance.csv')

# Create a heat map of the difference matrix with significance levels
sns.heatmap(diff_df, cmap='RdYlBu_r', center=0, fmt=".2g", cbar=False)
plt.show()
#annot=p_values