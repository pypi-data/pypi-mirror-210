import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

# Read the CSV file into a DataFrame
df = pd.read_csv('MRes Data/EEG Data/Coherence/Processed Coherence/final theta.csv', index_col=0)

# Convert the DataFrame to a NumPy array
coherence_matrix = df.to_numpy()

# Get the electrode names from the index of the DataFrame
electrodes = df.index.values

# Create a Matplotlib figure and axis objects for the two subplots
#fig, ((ax2, ax1), (ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(12,12))

fig, (ax2,ax1)= plt.subplots(nrows=1, ncols=2, figsize=(12,6))

# Create a colorbar object using the imshow() function and set the colormap to 'viridis'
im1 = ax1.imshow(coherence_matrix, cmap='viridis')

# Set the tick labels for the x-axis and y-axis to be the electrode names
ax1.set_xticks(np.arange(len(electrodes)))
ax1.set_yticks(np.arange(len(electrodes)))
ax1.set_xticklabels(electrodes)
ax1.set_yticklabels(electrodes)

# Rotate the x-axis tick labels by 90 degrees to avoid overlapping
plt.setp(ax1.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")

# Loop through the coherence matrix and add an asterisk to the corresponding position in the plot if the coherence value is greater than 0.7
for i in range(len(electrodes)):
    for j in range(len(electrodes)):
        if coherence_matrix[i,j] > 0.71:
            ax1.text(j, i, "*", ha="center", va="center", color="black", fontsize=16)

# Add a colorbar to the first plot using the colorbar() function
cbar1 = fig.colorbar(im1, ax=ax1)

# Set the labels for the colorbar
cbar1.set_label('Coherence')

legend_elements = [plt.scatter([], [], marker='*', c='k', alpha=0.5, s=80, label='< 70%')]
ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.65, -0.2), fontsize=20)

# Add 'a)' to the top left of the plot
ax1.text(-0.2, 1.08, "b)", transform=ax1.transAxes, size=20)

# Adjust the spacing between the subplots
plt.subplots_adjust(wspace=0.3)

# Show the plot

# Load the image and convert it to grayscale
img = Image.open("ROI Headmap.png").convert('L')
img_arr = np.array(img)

# Define the 1020 EEG system of electrodes with their corresponding significance and coordinates
electrodes = [('RF', 0.001, 490, 208),
              ('MF', 0.01, 330, 208),
              ('LF', 0.001, 175, 208),
              ('LFC', 0.008, 149, 345),
              ('MFC', 0.04, 330, 345),
              ('RFC', 0.01, 500, 345),
              ('LCP', 0.03, 145, 465),
              ('MCP', 0.09, 330, 465),
              ('RCP', 0.06, 500, 465),
              ('LPO', 0.1, 175, 580),
              ('RPO', 0.08, 490, 580),
              ('MPO', 0.3, 330, 600),]

# Unpack the electrode information into separate lists
electrode_labels, significance_values, x_coords, y_coords = zip(*electrodes)

# Create a figure and add the image as a background

ax2.imshow(img_arr, cmap='gray', alpha=0.5)

# Set the colors based on the significance values
colors = []
for val in significance_values:
    if val < 0.01:
        colors.append('blue')
    elif val < 0.05:
        colors.append('green')
    else:
        colors.append('#EEEEEE')

legend_elements = [plt.scatter([], [], marker='o', c='b', alpha=0.5, s=400, label='p < 0.01'),
                   plt.scatter([], [], marker='o', c='g', alpha=0.5, s=400, label='p < 0.05')]

#ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 0.5), fontsize=16)
ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.65, 0), fontsize=20)

ax2.text(-1.8, 1.08, "a)", transform=ax1.transAxes, size=20)

# Create a color map plot on top of the image based on significance values
vmin = min(significance_values)
vmax= max(significance_values)
im = ax2.scatter(x_coords, y_coords, s=3200, c=colors, alpha=0.5, vmin=vmin, vmax=vmax)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.axis('off')

fig.set_facecolor('#E5DEDB')


# Add the electrode labels to the plot
for i in range(len(electrodes)):
    ax2.text(x_coords[i], y_coords[i], electrode_labels[i], fontsize=25, ha='center', va='center')

# Add an arrow between AF3 and CP1
'''af3_x, af3_y = x_coords[12], y_coords[12]  # AF3 coordinatse
cp1_x, cp1_y = x_coords[17], y_coords[17]  # CP1 coordinates
ax2.annotate("", xy=(cp1_x, cp1_y), xytext=(af3_x, af3_y), arrowprops=dict(arrowstyle="->", color="black"),)
ax2.annotate("", xy=(af3_x, af3_y), xytext=(-5, 5), textcoords="offset points", fontsize=8, ha='right', va='bottom',)
ax2.annotate("", xy=(cp1_x, cp1_y), xytext=(-5, 5), textcoords="offset points", fontsize=8, ha='right', va='bottom',)
'''
plt.show()
