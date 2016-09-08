"""
This module holds helper functions for use with the pandas package
"""

import logging
import pandas as pd
import numpy as np
import itertools

def printall(df, max_rows = 999, max_colwidth=200):
    """prints the entire dataframe (up to max_rows) and returns to original context"""
    with pd.option_context('display.max_rows', max_rows, 'display.max_colwidth', max_colwidth):
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
    axis = None, 0 (columns), or 1 (rows)
    """
    assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
    assert axis in [None, 0, 1], "axis parameter must be either None, 0, or 1"
    if axis is None:
        return df.div(df.sum().sum())
    elif axis==0:
        return df.div(df.sum(axis=0), axis=1)
    elif axis==1:
        return df.div(df.sum(axis=1), axis=0)

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
    elif type(colname) is not str:
        logging.warn("The column name or keyword supplied was not a string, returning original series")
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


def complete_index(df, **kwargs):
    """
    complete the index of the dataframe with all possible values of the different levels of the index

    Parameters
    ----------
    df: pandas datafrmae
        the dataframe for which the index will be completed

    **kwargs: 
        keyword arguments to the panads DataFrame reindex() method

    Output
    ------
    A pandas DataFrame with the completed index
    """

    assert isinstance(df.index, pd.MultiIndex)
    all_idx = itertools.product(*[y.values for y in df.index.levels])
    
    return df.reindex(pd.MultiIndex.from_tuples(list(all_idx)), **kwargs)


def bins_from_points(cutoffs, lbound=-np.inf, ubound=np.inf):
    """
    Creates a list that can be input into binning functions such as pd.cut from points of the cutoffs
    
    Parameters
    ----------
    cutoffs: list
        list of cutoff points 
        
    lbound: float or int (optional)
        lower bound of the bins
    ubound: float or int (optional)
        upper bound of the bins
    """
    return [lbound]+sorted(cutoffs)+[ubound]
    
def cutagg(ser_list, cuts, values=None, agg_function=np.sum):
    """
    Cuts the values into binned groups defined by the cuts parameter applied to the ser_list
    and aggregates by agg_function column-wise
    
    Parameters:
    -----------
    ser_list: list
            list of iterables (float or int) to cut up to determine groups
            
    cuts:     list of lists
            list (same length as ser_list) of a list of cutoffs to use on the series associated by position
            
    values:   pandas Series or DataFrame (optional)
            Pandas series or dataframe which to aggregate -- must have groupby() method
            
    agg_function:  function or dict (default np.sum)
            Function to use for aggregating groups. If a function, must either work when passed a DataFrame or when passed to DataFrame.apply. If passed a dict, the keys must be DataFrame column names.
            Accepted Combinations are:
            string cythonized function name
            function
            list of functions
            dict of columns -> functions
            nested dict of names -> dicts of functions

                        
    Default behavior:
    -----------------
    it counts the number of observations in each series-cut
    """
    # check that all series lengths are equal
    series_lengths = [len(x) for x in ser_list]
    assert series_lengths.count(series_lengths[0]) == len(series_lengths)
    
    # make values column of all ones (equivalent to count) if none was given
    values = pd.Series(np.ones(series_lengths[0])) if values is None else values
    
    grps = [pd.cut(x, c) for c, x in zip(cuts, ser_list)]
    
    return values.groupby(grps).agg(np.sum)


def pretty_interval(interval_string, return_type="both", return_concat=" & "):
    """
    Prettifies interval strings like '(0, 3]' to use <= and > and >= and < 
    
    Parameters
    ----------
    interval_string: string
        a string like (0, 2] that represents an interval (usually output by pandas.cut)
    return_type: string (either 'both', 'right', or 'left')
        both: return both the left and right boundaries in the output string
        right: return just the right (upper) output boundary as a string
        left: return just the left (lower) output boundary as a string
    return_concat: string
        if return_type=='both', a string to separate the lower and upper bounds in the output
        
        
    >>>pretty_interval('(0, 3]')
    >>>">0 & <=3"
    
    >>>pretty_interval("[9, 12]", return_type="right")
    >>>"<=12"
    
    >>>pretty_interval("(0, 4)", return_concat="and")
    >>>">0 and <4"
    """
    s1, s2 = interval_string.split(",")
    s1_id, s1_num = s1[0], s1[1:]
    s2_id, s2_num = s2[-1], s2[:-1]
    d = {"(":">", "[":">=", ")":"<", "]":"<="}
    s2_id = d[s2_id]
    s1_id = d[s1_id]
    
    l = s1_id+s1_num
    r = s2_id+s2_num
    if return_type=='both':
        return return_concat.join([l, r])
    elif return_type=='right':
        return r
    elif return_type=="left":
        return l
    else:
        raise KeyError("return_type must be one of 'both', 'right', or 'left'")


def multi_groupby(df, groupby, func, nafill="---"):
    """groups by each combination of the groupby -- each level separately

    Parameters
    ----------
    df -- dataframe or series, 
    groupby -- list of series 
    func -- function to apply to each group
    nafill -- string, string to fill na in the returning index

    Output
    ------
    dataframe

    Dataframe with the index filled with <nafill> for higher order aggregation functions

    """
    allcombos = []
    index_names = set()
    for r in xrange(1,len(groupby)+1):
        for combo in itertools.combinations(range(len(groupby)), r):
            grouped = df.groupby([groupby[i] for i in combo]).apply(func)
            index_names.update(set(grouped.index.names))
            allcombos.append(grouped.reset_index())
    return pd.concat(allcombos).fillna(nafill).set_index(list(index_names))