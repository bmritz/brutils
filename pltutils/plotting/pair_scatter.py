import seaborn as sns


def pair_scatter(df, **kwargs):
    """
    pair_scatter

    This takes the same args and kwargs that seaborn.pairplot does

    This is mostly just like seaborn.pairplot, but outputs a figure instead of the PairPlot object
    """

    grid = sns.pairplot(df, **kwargs)
    return grid.fig