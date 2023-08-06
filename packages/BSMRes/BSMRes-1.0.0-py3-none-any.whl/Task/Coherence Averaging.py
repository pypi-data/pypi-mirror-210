import os
import pandas as pd

# Set the directory containing the CSV files
csv_dir = 'MRes Data/EEG Data/Coherence/Theta/Low'

# Get a list of all CSV files in the directory
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# Read in each CSV file and calculate the average coherence matrix
n_files = len(csv_files)
coherence_sum = None
for i, csv_file in enumerate(csv_files):
    # Load the coherence matrix from the CSV file
    coherence_df = pd.read_csv(os.path.join(csv_dir, csv_file), index_col=0)
    

    # Add the coherence matrix to the running sum
    if coherence_sum is None:
        coherence_sum = coherence_df
    else:
        coherence_sum += coherence_df

    # Print progress
    print(csv_file + '\n' + '\n' + f'Read {i+1} of {n_files} CSV files' + '\n')

# Calculate the average coherence matrix
coherence_avg = coherence_sum / n_files


coherence_avg.to_csv('MRes Data/EEG Data/Coherence/Processed Coherence/Theta H Coherence.csv')

csv_dir = 'MRes Data/EEG Data/Coherence/Theta'

# Get a list of all CSV files in the directory
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# Read in each CSV file and calculate the average coherence matrix
n_files = len(csv_files)
coherence_sum = None
for i, csv_file in enumerate(csv_files):
    # Load the coherence matrix from the CSV file
    coherence_df = pd.read_csv(os.path.join(csv_dir, csv_file), index_col=0)

    # Add the coherence matrix to the running sum
    if coherence_sum is None:
        coherence_sum = coherence_df
    else:
        coherence_sum += coherence_df

    # Print progress
    print(csv_file + '\n' + '\n' + f'Read {i+1} of {n_files} CSV files' + '\n')

# Calculate the average coherence matrix
coherence_avg = coherence_sum / n_files


coherence_avg.to_csv('MRes Data/EEG Data/Coherence/Processed Coherence/Theta L Coherence.csv')

'''df1 = pd.read_csv('D:\MRes Data\EEG Data\Coherence\Processed Coherence/LC Coherence.csv')
df4 = pd.read_csv('D:\MRes Data\EEG Data\Coherence\Processed Coherence/GC Coherence.csv')
result = pd.concat([df1, df4], axis=1, join="inner")

'''
