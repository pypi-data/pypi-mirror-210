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

fig, (ax2,ax1)=plt.subplots(nrows=1, ncols=2, figsize=(10,5))

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
        if coherence_matrix[i,j] > 0.7:
            ax1.text(j, i, "*", ha="center", va="center", color="black")

# Add a colorbar to the first plot using the colorbar() function
cbar1 = fig.colorbar(im1, ax=ax1)

# Set the labels for the colorbar
cbar1.set_label('Coherence')

legend_elements = [plt.scatter([], [], marker='*', c='k', alpha=0.5, s=30, label='< 70%')]
ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.65, -0.2), fontsize=12)

# Add 'a)' to the top left of the plot
ax1.text(-0.2, 1.08, "c)", transform=ax1.transAxes, size=20)

# Adjust the spacing between the subplots
plt.subplots_adjust(wspace=0.3)

# Show the plot

# Load the image and convert it to grayscale
img = Image.open('MRes Data/EEG Data/Coherence/Processed Coherence/EEG Map2.png').convert('L')
img_arr = np.array(img)

# Define the 1020 EEG system of electrodes with their corresponding significance and coordinates
electrodes = [('Fp1*', 0.041, 156, 51),
              ('Fp2*', 0.01, 225.90, 51),
              ('F7**', 0.001, 76, 98),
              ('F3*', 0.07, 134.40, 125),
              ('Fz*', 0.04, 191, 131.25),
              ('F4*', 0.01, 244.60, 125.25),
              ('F8**', 0.001, 302.80, 98.25),
              ('T7', 0.06, 51.20, 207.35),
              ('C3', 0.06, 116.40, 209.35),
              ('Cz', 0.1, 187.50, 205.35),
              ('C4*', 0.04, 258.60, 206.35),
              ('T8', 0.3, 337.80, 205.35),
              ('AF3*', 0.04, 147.15, 86.45),
              ('P3*', 0.04, 133.35, 286.45),
              ('Pz*', 0.05, 190.50, 285.45),
              ('P4', 0.3, 246.65, 290.45),
              ('FC6*', 0.04, 291.85, 160.45),
              ('CP1*', 0.04, 160.30, 250.60),
              ('CP2*', 0.04, 223.70, 250.60),
              ('PO3', 0.4, 158.85, 326.45),
              ('PO4', 0.38, 225.30, 326.60),
              ('P7*', 0.04, 80.70, 317.60),
              ('CP6', 0.4, 290.85, 254.45),
              ('O1*', 0.045, 156.30, 362.60),
              ('O2', 0.5, 225.70, 362.60),
              ('PO7', 0.34, 106.30, 356.60),
              ('PO8', 0.06, 280.30, 356.60),
              ('P8', 0.07, 303.30, 316.60),
              ('CP5', 0.35, 90.30, 259.60),
              ('FC1', 0.3, 160.30, 169.60),
              ('FC2**', 0.001, 222.30, 169.60),
              ('AF4*', 0.02, 236.30, 90.60),
              ('FPz*', 0.02, 192.30, 52.60),
              ('FC5**', 0.001, 89.30, 160.60),
              ('Oz', 0.3, 190.30, 363.60), ]

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
        colors.append('red')

legend_elements = [plt.scatter([], [], marker='o', c='b', alpha=0.5, s=100, label='p < 0.01'),
                   plt.scatter([], [], marker='o', c='g', alpha=0.5, s=100, label='p < 0.05')]
#ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 0.5), fontsize=16)
ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.65, -0.05), fontsize=16)

ax2.text(-1.8, 1.08, "b)", transform=ax1.transAxes, size=20)

# Create a color map plot on top of the image based on significance values
vmin = min(significance_values)
vmax= max(significance_values)
im = ax2.scatter(x_coords, y_coords, s=1200, c=colors, alpha=0.5, vmin=vmin, vmax=vmax)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.axis('off')

fig.set_facecolor('#E5DEDB')


# Add the electrode labels to the plot
for i in range(len(electrodes)):
    ax2.text(x_coords[i], y_coords[i], electrode_labels[i], fontsize=12, ha='center', va='center')

# Add an arrow between AF3 and CP1
'''af3_x, af3_y = x_coords[12], y_coords[12]  # AF3 coordinatse
cp1_x, cp1_y = x_coords[17], y_coords[17]  # CP1 coordinates
ax2.annotate("", xy=(cp1_x, cp1_y), xytext=(af3_x, af3_y), arrowprops=dict(arrowstyle="->", color="black"),)
ax2.annotate("", xy=(af3_x, af3_y), xytext=(-5, 5), textcoords="offset points", fontsize=8, ha='right', va='bottom',)
ax2.annotate("", xy=(cp1_x, cp1_y), xytext=(-5, 5), textcoords="offset points", fontsize=8, ha='right', va='bottom',)
'''
plt.show()
