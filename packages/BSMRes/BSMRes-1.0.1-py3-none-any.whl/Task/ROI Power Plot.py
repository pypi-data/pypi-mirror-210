import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

fig, ax2 = plt.subplots(figsize=(8, 10))

# Load the image and convert it to grayscale
img = Image.open("ROI Headmap.png").convert('L')
img_arr = np.array(img)

# Define the 1020 EEG system of electrodes with their corresponding significance and coordinates
electrodes = [('RF', 0.001, 490, 208),
              ('MF', 0.0001, 330, 208),
              ('LF', 0.03, 175, 208),
              ('LFC', 0.08, 149, 345),
              ('MFC', 0.04, 330, 345),
              ('RFC', 0.0001, 500, 345),
              ('LCP', 0.9, 145, 465),
              ('MCP', 0.9, 330, 465),
              ('RCP', 0.5, 500, 465),
              ('LPO', 0.0001, 175, 580),
              ('RPO', 0.08, 490, 580),
              ('MPO', 0.5, 330, 600),]

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
        colors.append('#E5DEDB')

'''legend_elements = [plt.scatter([], [], marker='o', c='b', alpha=0.5, s=400, label='p < 0.01'),
                   plt.scatter([], [], marker='o', c='g', alpha=0.5, s=400, label='p < 0.05')]

#ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 0.5), fontsize=16)
ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.65, 0), fontsize=20)'''

#ax2.text(-1.8, 1.08, "a)", transform=ax2.transAxes, size=26)

# Create a color map plot on top of the image based on significance values
vmin = min(significance_values)
vmax= max(significance_values)
im = ax2.scatter(x_coords, y_coords, s=2000, c=colors, alpha=0.5, vmin=vmin, vmax=vmax)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.axis('off')

#fig.set_facecolor('#E5DEDB')


# Add the electrode labels to the plot
for i in range(len(electrodes)):
    ax2.text(x_coords[i], y_coords[i], electrode_labels[i], fontsize=20, ha='center', va='center')

'''ax2.text(-0.1, 1.05, "a)", transform=ax2.transAxes, size=20)
ax2.text(0.2, 1.05, "Low Theta", transform=ax2.transAxes, size=26)'''

plt.show()
