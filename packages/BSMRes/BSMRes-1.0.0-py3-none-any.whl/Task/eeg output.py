# Open the text file for reading
with open('D:/MRes Data/EEG Data/1 - H.txt', 'r') as f:
    # Read all lines into a list
    lines = f.readlines()
print(lines)

# Remove any newline characters from each line
lines = [line.strip() for line in lines]

# Move each next row to the previous row
merged = '\t'.join(lines)

# Export the data to a CSV file with tab delimiter
with open('D:/MRes Data/EEG Data/eeg data.csv', 'w') as f:
    # Write the merged data with tab delimiter
    f.write('\t'.join(merged.split()) + '\n')
