import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

#creates a heatmap from data into target location
def plot(data, target):

    fig, ax = plt.subplots(figsize=(25,25))
    im = ax.imshow(data)

    x = len(data)
    y = len(data[0])

    # Loop over data dimensions and create text annotations.
    for i in range(x):
        for j in range(y):
            text = ax.text(j, i, data[i][j],
                        ha="center", va="center", color="w")

    ax.set_title("Heatmap of the Scores")
    fig.tight_layout()
    plt.savefig(target)


def barchart_rule_count(data, target):

    print(data)
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(25,15))

    labels = list(data.keys())
    values = list(data.values())
    values = list(np.array(values)[:,1])

    y_pos = np.arange(len(labels))

    ax.barh(y_pos, values, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('#Times used')
    ax.set_title('Rule Frequency')
    ax.set_xscale('log')

    plt.savefig(target)

