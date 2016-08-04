"""
This module holds helper functions for use with the pandas package
"""

import pandas as pd
import collections
import logging


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
    else:
        raise ValueError, "axis parameter must be None, 0, or 1"

# def norm_horz(df):
#     """
#     Normalize each
#     assert np.all(df>=0), "DataFrame input into norm_horz must have all elements >=0"
#     return df.div(df.sum(axis=1), axis=0)

# def norm_vert(df):
#     assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
#     return df.div(df.sum(axis=0), axis=1)


def merge_on_multiindex(left, right, how="left", sort=False, suffixes=("_x", "_y"), copy=True, indicator=False):
    """
    Merge two dataframes on their index when they both have a multindex
    indexes must have the same names to be merged
    index of result will be the overlap of both indicies in the order of the left index
    """
    index_names = [name for name in left.index.names if name in right.index.names]
    return pd.merge(left.reset_index(), right.reset_index(), 
            how=how, sort=sort, suffixes=suffixes, copy=copy, indicator=indicator).set_index(index_names)

DOLLAR = "${:,.2f}".format
WHOLE = "{:,.0f}".format
PCT = "{:,.0f}%".format

def fmt_col(df, colname):
    if df[colname].dtype == 'O':
        logging.debug("The column was dtype 'O', returning original column")
        return df[colname]
    else:
        if 'per' in colname:
            checkstr = colname.split('per')[0]
        elif '/' in colname:
            checkstr = colname.split('/')
        else:
            checkstr = colname

        if 'sales' in checkstr.lower():
            # return the sales format
            return df[colname].map(SALES)
        elif any(x in checkstr.lower() for x in ['unit', 'visit', 'customer']):
            # return whole format
            return df[colname].map(WHOLE)
        elif any(x, in checkstr.lower() for x in ['sor', 'share', 'requirement', 'pct', 'percent']):
            assert (df[colname]<=1).all(), "Function fmt_col detected a percentage column name but the values were not <= 1."
            # return percentage format
            return df[colname].map(PCT)


def chunk_col_values(filename, column, delimiter=",", sorted=True, maxkeys=1):
    """
    returns an iterator that chunks the file on a column value

    TODO: 
    Progress bar

    """

    # iterate through the column and construct a dict of the start and end indexes
    if isinstance(column, str):
        column = [column]

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter) 
        rownum = 0
        # index_dict = collections.defaultdict(lambda: [None,None])
        colnames = reader.next()
        colnums = [colnames.index(c) for c in colnames if c in column]

        if sorted:
            first = rownum
            prev_row = reader.next()
            prev_key = tuple([prev_row[c] for c in colnums])
            i = 0
            for row in reader:
                rownum+=1
                key = tuple([row[c] for c in colnums])
                if key != prev_key:
                    i+=1
                    if i >= maxkeys:
                        last = rownum-1
                        i = 0
                        yield pd.read_csv(filename, delimiter=delimiter, names=colnames, skiprows=first, nrows=last-first+1, header=0)
                        first = rownum
                prev_key = key
        else:
            raise NotImplementedError