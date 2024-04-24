from matplotlib import pyplot as plt
from pandas import DataFrame

def dispertion(df: DataFrame, columns: object, labels: object, title: str, color: str="purple", range: tuple=None):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[columns["x"]], df[columns["y"]], color=color)
    plt.xlim(range)
    plt.xlabel(labels["x"])
    plt.ylabel(labels["y"])
    plt.title(title)
    plt.show()
