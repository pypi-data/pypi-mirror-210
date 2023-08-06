import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

img = Image.open("ROI Headmap.png").convert('L')
img_arr = np.array(img)

fig, (ax2,ax1)=plt.subplots(nrows=1, ncols=2, figsize=(10,5))

'''electrodes = [('', 90.001, 490, 208),
              ('', 90.01, 330, 208),
              ('', 90.001, 175, 208),
              ('', 90.008, 149, 345),
              ('', 90.04, 330, 345),
              ('', 90.01, 500, 345),
              ('', 90.03, 145, 465),
              ('', 90.09, 330, 465),
              ('', 90.06, 500, 465),
              ('', 90.1, 175, 580),
              ('', 90.08, 490, 580),
              ('', 90.3, 330, 600),]'''

electrodes = [('RF', 0.01, 490, 208),
              ('MF', 0.01, 330, 208),
              ('LF', 0.01, 175, 208),
              ('LFC', 90.01, 149, 345),
              ('MFC', 0.01, 330, 345),
              ('RFC', 0.01, 500, 345),
              ('LCP', 09.03, 145, 465),
              ('MCP', 09.09, 330, 465),
              ('RCP', 09.06, 500, 465),
              ('LPO', 0.01, 175, 580),
              ('RPO', 09.08, 490, 580),
              ('MPO', 09.01, 330, 600),]

# Unpack the electrode information into separate lists
electrode_labels, significance_values, x_coords, y_coords = zip(*electrodes)

# Create a figure and add the image as a background

ax1.imshow(img_arr, cmap='gray', alpha=0.5)

# Set the colors based on the significance values
colors = []
for val in significance_values:
    if val < 0.01:
        colors.append('blue')
    elif val < 0.05:
        colors.append('gray')
    else:
        colors.append('gray')
        #colors.append('#EEEEEE')

legend_elements = [plt.scatter([], [], marker='o', c='b', alpha=0.5, s=400, label=''),
                   plt.scatter([], [], marker='o', c='g', alpha=0.5, s=400, label='')]


ax1.text(-1.8, 1.05, "b)", transform=ax1.transAxes, size=20)

# Create a color map plot on top of the image based on significance values
vmin = min(significance_values)
vmax= max(significance_values)
im = ax1.scatter(x_coords, y_coords, s=2000, c=colors, alpha=0.5, vmin=vmin, vmax=vmax)
ax1.set_xticks([])
ax1.set_yticks([])
ax1.axis('off')

#fig.set_facecolor('#E5DEDB')

for i in range(len(electrodes)):
    ax1.text(x_coords[i], y_coords[i], electrode_labels[i], fontsize=0, ha='center', va='center')
    circle = plt.Circle((x_coords[i], y_coords[i]), 10, color='white', alpha=0.8)
    ax1.add_artist(circle)

lf_index = electrode_labels.index('LF')
rf_index = electrode_labels.index('RF')
mf_index = electrode_labels.index('MF')
lfc_index = electrode_labels.index('LFC')
rfc_index = electrode_labels.index('RFC')
mfc_index = electrode_labels.index('MFC')
lpo_index = electrode_labels.index('LPO')
mpo_index = electrode_labels.index('MPO')


lf_x, lf_y = x_coords[lf_index], y_coords[lf_index]
rf_x, rf_y = x_coords[rf_index], y_coords[rf_index]
mf_x, mf_y = x_coords[mf_index], y_coords[mf_index]
lfc_x, lfc_y = x_coords[lfc_index], y_coords[lfc_index]
rfc_x, rfc_y = x_coords[rfc_index], y_coords[rfc_index]
mfc_x, mfc_y = x_coords[mfc_index], y_coords[mfc_index]
lpo_x, lpo_y = x_coords[lpo_index], y_coords[lpo_index]
mpo_x, mpo_y = x_coords[mpo_index], y_coords[mpo_index]


#ax1.plot([330, lf_x], [287, lf_y], 'g-', linewidth=4)
#ax1.plot([330, mf_x], [287, mf_y], 'g-', linewidth=4)
#ax1.plot([330, rf_x], [287, rf_y], 'g-', linewidth=4)
ax1.plot([mf_x, lfc_x], [mf_y, lfc_y], 'g-', linewidth=4)
ax1.plot([rfc_x, rf_x], [rfc_y, rf_y], 'g-', linewidth=4)
ax1.plot([rfc_x, rf_x], [rfc_y, rf_y], 'g-', linewidth=4)
#ax1.plot([lfc_x, lpo_x], [lfc_y, lpo_y], 'k-', linewidth=4)
#ax1.plot([lfc_x, mfc_x], [lfc_y, mfc_y], 'k-', linewidth=4)
#ax1.plot([lpo_x, mpo_x], [lpo_y, mpo_y], 'k-', linewidth=4)
#ax1.plot([lfc_x, mfc_x], [lfc_y, mfc_y], 'k-', linewidth=4)
ax2.plot([lpo_x, lfc_x], [lpo_y, lfc_y], 'g-', linewidth=4)

ax1.text(.4, 1.05, "20-30 Hz", transform=ax1.transAxes, size=20)

ax1.text(-0.1, 1.05, "b)", transform=ax1.transAxes, size=20)


# Define the 1020 EEG system of electrodes with their corresponding significance and coordinates
'''electrodes = [('', 90.001, 490, 208),
              ('', 90.01, 330, 208),
              ('', 90.001, 175, 208),
              ('', 90.008, 149, 345),
              ('', 90.04, 330, 345),
              ('', 90.01, 500, 345),
              ('', 90.03, 145, 465),
              ('', 90.09, 330, 465),
              ('', 90.06, 500, 465),
              ('', 90.1, 175, 580),
              ('', 90.08, 490, 580),
              ('', 90.3, 330, 600),]'''

electrodes = [('RF', 0.01, 490, 208),
              ('MF', 0.01, 330, 208),
              ('LF', 0.01, 175, 208),
              ('LFC', 0.01, 149, 345),
              ('MFC', 0.01, 330, 345),
              ('RFC', 0.01, 500, 345),
              ('LCP', 09.03, 145, 465),
              ('MCP', 09.09, 330, 465),
              ('RCP', 09.06, 500, 465),
              ('LPO', 0.01, 175, 580),
              ('RPO', 09.08, 490, 580),
              ('MPO', 0.01, 330, 600),]

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
        colors.append('gray')
    else:
        colors.append('gray')
        #colors.append('#EEEEEE')

legend_elements = [plt.scatter([], [], marker='o', c='b', alpha=0.5, s=400, label=''),
                   plt.scatter([], [], marker='o', c='g', alpha=0.5, s=400, label='')]


ax2.text(-1.8, 1.05, "a)", transform=ax2.transAxes, size=20)

# Create a color map plot on top of the image based on significance values
vmin = min(significance_values)
vmax= max(significance_values)
im = ax2.scatter(x_coords, y_coords, s=2000, c=colors, alpha=0.5, vmin=vmin, vmax=vmax)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.axis('off')

#fig.set_facecolor('#E5DEDB')

for i in range(len(electrodes)):
    ax2.text(x_coords[i], y_coords[i], electrode_labels[i], fontsize=0, ha='center', va='center')
    circle = plt.Circle((x_coords[i], y_coords[i]), 10, color='white', alpha=0.8)
    ax2.add_artist(circle)

lf_index = electrode_labels.index('LF')
rf_index = electrode_labels.index('RF')
mf_index = electrode_labels.index('MF')
lfc_index = electrode_labels.index('LFC')
rfc_index = electrode_labels.index('RFC')
mfc_index = electrode_labels.index('MFC')
lpo_index = electrode_labels.index('LPO')
mpo_index = electrode_labels.index('MPO')

lcp_index = electrode_labels.index('LCP')


lf_x, lf_y = x_coords[lf_index], y_coords[lf_index]
rf_x, rf_y = x_coords[rf_index], y_coords[rf_index]
mf_x, mf_y = x_coords[mf_index], y_coords[mf_index]
lfc_x, lfc_y = x_coords[lfc_index], y_coords[lfc_index]
rfc_x, rfc_y = x_coords[rfc_index], y_coords[rfc_index]
mfc_x, mfc_y = x_coords[mfc_index], y_coords[mfc_index]
lpo_x, lpo_y = x_coords[lpo_index], y_coords[lpo_index]
mpo_x, mpo_y = x_coords[mpo_index], y_coords[mpo_index]

lcp_x, lcp_y = x_coords[lcp_index], y_coords[lcp_index]


'''ax2.plot([330, lf_x], [287, lf_y], 'g-', linewidth=4)
ax2.plot([330, mf_x], [287, mf_y], 'g-', linewidth=4)
ax2.plot([330, rf_x], [287, rf_y], 'g-', linewidth=4)
ax2.plot([330, mfc_x], [287, mfc_y], 'g-', linewidth=4)'''
#ax2.plot([rfc_x, rf_x], [rfc_y, rf_y], 'g-', linewidth=4)
#ax2.plot([rfc_x, mfc_x], [rfc_y, mfc_y], 'r-', linewidth=4)
ax2.plot([mpo_x, mfc_x], [mpo_y, mfc_y], 'g-', linewidth=4)
#ax2.plot([lfc_x, mfc_x], [lfc_y, mfc_y], 'g-', linewidth=4)
ax2.plot([lpo_x, mpo_x], [lpo_y, mpo_y], 'r-', linewidth=4)
ax2.plot([mfc_x, rfc_x], [mfc_y, rfc_y], 'g-', linewidth=4)
ax1.plot([lcp_x, rf_x], [lcp_y, rf_y], 'g-', linewidth=4)
ax2.plot([lpo_x, rf_x], [lpo_y, rf_y], 'g-', linewidth=4)

ax2.text(.4, 1.05, "12-20 Hz", transform=ax2.transAxes, size=20)

ax2.text(-0.1, 1.05, "a)", transform=ax2.transAxes, size=20)

plt.show()
