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


def to_html_float_left(dfs, titles=None, padding_left=10):
    """
    Show dataframes side by side using the float:left style of divs
    
    Args:
    dfs: list of dataframes to show
    titles: (optional) list of strings that represent the titles of the dataframes,
                if supplied, must be same length as dfs
    padding_left: the padding between the dataframes (px)
                
    Output:
    string: the html string representing the dataframes side by side
            wrap this string into IPython.display.HTML(<string>) to display in notebook
    """
    
    if titles is not None:
        assert len(titles)==len(dfs), "Length of titles must be same length as dfs"
    else:
        titles = ["DF %s" % i for i, x in enumerate(dfs)]
    
    html = ''
    for i, (k, v) in enumerate(zip(titles, dfs)):
        if i > 0:
            p = padding_left
        else:
            p = 10
        html += ('''<div style=\"float:left; padding-left:{}px;\">
                 <strong>{}</strong>{}</div>'''
                 .format(p, k , v.to_html()))
    return '<div style="float:left; width:100%;">' + html + '</div>'

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
PCT = "{:.0%}".format

def fmt_series_retail(series, keyword=None):
    """
    Parameters
    ----------
    series : pandas series
        The series which you would like formatted, 
        The name of the series will be used as the keyword if keyword is None
        If both the name of hte series and the keyword parameter are None, the function will error
    keyword = None: str, optional
        The keyword that the function will attempt to match to an internal lookup to 
        determine which type of format to use
        Examples could be: 'Customer', 'visits', 'units'
        Case insensitive
        If None (default), the keyword defaults to the name of the series
    """
    colname = keyword or series.name

    if series.dtype == 'O':
        logging.debug("The series was dtype 'O', returning original series")
        return series
    elif colname is None:
        logging.warn("There was no name for the series, and no keyword supplied, returning original series")
        return series
    else:
        if 'per' in colname:
            checkstr = colname.split('per')[0]
        elif '/' in colname:
            checkstr = colname.split('/')
        else:
            checkstr = colname

        if (series<=1).all():
            return series.map(PCT)
        elif any(x in checkstr.lower() for x in ['sales', 'spend']):
            return series.map(DOLLAR)
        elif any(x in checkstr.lower() for x in ['unit', 'visit', 'customer']):
            return series.map(WHOLE)
        elif any(x in checkstr.lower() for x in ['sor', 'share', 'requirement', 'pct', 'percent']):
            assert (series<=1).all(), "Function fmt_col detected a percentage column name but the values were not <= 1."
            return series.map(PCT)
        else:
            logging.warn("The series name or keyword was not found in the lookup, returning original series")
            return series


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
