import matplotlib.pyplot as plt

# Define the data for the pie charts
data1 = [53.4, 46.6]
labels1 = ['', '']

data2 = [89.9,10.1]
labels2 = ['', '']

# Define the colors for the slices

colors1 = ['#338FF5', '#75B572'] 


# Create the subplots
fig, axs = plt.subplots(2, 1, figsize=(6, 8))
fig.set_facecolor('#E5DEDB')


# Create the pie charts in each subplot with custom colors and larger label size
axs[0].pie(data1, labels=labels1, autopct='%1.1f%%', colors=colors1, textprops={'fontsize': 26})
axs[0].set_title('Goal Conflict Accuracy', size=20)
axs[0].text(-0.2, 1.08, "c)", transform=axs[0].transAxes, size=20)


axs[1].pie(data2, labels=labels2, autopct='%1.1f%%', colors=colors1, textprops={'fontsize': 19})
axs[1].set_title('Low Conflict Accuracy', size=20)

# Adjust the layout
plt.tight_layout()

# Show the plot
plt.show()
