"""
This module holds helper functions for use with the pandas package
"""

import pandas as pd

def printall(df, max_rows = 999):
    """prints the entire dataframe (up to max_rows) and returns to original context"""
    with pd.option_context('display.max_rows', 999):
        print df

def split_string(string_series, delim=" "):
    """
    splits the string series into multiple series based on the delimiter
    returns generator object of series

    if you want a tuple then call tuple(split_string(<string series>))

    you can assign to new columns like:
    df['newcol1'], df['newcol2'] = split_string(df['delimited string col'])
    """
    orig_index = string_series.index
    #tups =  zip(*string_series.apply(lambda x: x.split(delim)))
    return (pd.Series(data=x, index=orig_index) for x in zip(*string_series.apply(lambda x: x.split(delim))))


def normalize(df, axis=None):
    """
    Normalize the dataframe or group on the selected axis
    axis = None, 0 (rows), or 1 (columns)
    """
    assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
    if axis is None:
        return df.div(df.sum().sum())
    elif axis==0:
        return df.div(df.sum(axis=0), axis=1)
    elif axis==1:
        return df.div(df.sum(axis=1), axis=0)


# def norm_horz(df):
#     """
#     Normalize each
#     assert np.all(df>=0), "DataFrame input into norm_horz must have all elements >=0"
#     return df.div(df.sum(axis=1), axis=0)

# def norm_vert(df):
#     assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
#     return df.div(df.sum(axis=0), axis=1)


