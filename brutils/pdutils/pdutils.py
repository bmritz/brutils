"""
This module holds helper functions for use with the pandas package
"""

import logging
import pandas as pd
import numpy as np
import itertools, copy
import json
from collections import OrderedDict

def df_from_ldjson(filename):
    all_lines = []
    with open(filename, "r") as fil:
        for line in fil:
            all_lines.append(json.loads(line))
    return pd.DataFrame(all_lines)
        

def printall(df, max_rows = 999, max_colwidth=200):
    """prints the entire dataframe (up to max_rows) and returns to original context"""
    with pd.option_context('display.max_rows', max_rows, 'display.max_colwidth', max_colwidth):
        print (df)

def english_join(seq):
    """ join a list of strings separated by commas with an 'and' contraction before the last value

    INPUTS:
    seq (list of strings)

    OUTPUTS:
    (string)
    """
    return ", ".join(seq[:-1]) + " and " + seq[-1]

def timedelta_to_english(td):
    info = OrderedDict()
    info["Days"] = td.days
    info["Hours"] = td.seconds // 3600
    info["Minutes"] = (td.seconds//60)%60
    res = []
    for lab, t in info.items():
        if t>0:
            if t==1:
                res.append(lab[:-1])
            else:
                res.append("%s %s" % (t, lab))
    return ", ".join(res)

def list_to_html(lst, list_type="unordered"):
    if list_type=='unordered':
        tg_open, tg_close = "<ul>", "</ul>"
    else:
        tg_open, tg_close = "<ol>", "</ol>"
        
    ret = [tg_open]
    
    for x in lst:
        if not isinstance(x, list):
            ret.append("<li>"+str(x)+"</li>")
        else:
            ret.append(list_to_html(x, list_type=list_type))
    ret.append(tg_close)
    #return tg_open + "".join(["<li>"+str(x)+"</li>" for x in lst]) + tg_close
    return "".join(ret)

def html_float_left(htmls, titles=None, padding_left=10):
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
        assert len(titles)==len(htmls), "Length of titles must be same length as dfs"
    else:
        titles = ["Figure %s" % i for i, x in enumerate(htmls)]
    
    html = ''
    for i, (k, v) in enumerate(zip(titles, htmls)):
        if i > 0:
            p = padding_left
        else:
            p = 10
        html += ('''<div style=\"float:left; padding-left:{}px;\">
                 <strong>{}</strong>{}</div>'''
                 .format(p, k , v))
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

def normalize(df, axis=None, strict=True):
    """
    Normalize the dataframe or group on the selected axis
    axis = None, 0 (columns), or 1 (rows)
    """
    if strict:
        assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
    assert axis in [None, 0, 1], "axis parameter must be either None, 0, or 1"
    if axis is None:
        return df.div(df.values.sum())
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
        try:
            left_cols = set(left.columns)
        except AttributeError:
            left = left.to_frame()
            return merge_on_multiindex(left, right, how=how, sort=sort, suffixes=suffixes, copy=copy, indicator=indicator)

        try:
            right_cols = set(right.columns)
        except AttributeError:
            right = right.to_frame()
            return merge_on_multiindex(left, right, how=how, sort=sort, suffixes=suffixes, copy=copy, indicator=indicator)
        

        assert len(left_cols.intersection(right_cols)) == 0
        index_names = [name for name in left.index.names if name in right.index.names]
        return pd.merge(left.reset_index(), right.reset_index(), 
                                on=index_names, how=how, sort=sort, suffixes=suffixes, copy=copy, indicator=indicator)\
                .set_index(list(OrderedDict.fromkeys(left.index.names + right.index.names)))


def iter_index_tuples(df):
    iter_index = (tuple(zip(df.index.names, x)) for x in df.index.values)
    return iter_index

def semijoin_index(df1, df2):
    """ filter the rows of df1 by the rows in df2 through the index

    return every row in df1 where the index of df1 matches the index of df2 on every level in df2
    every level of  df2 must be in df1

    """
    common_levels = set(df1.index.names).intersection(df2.index.names)
    assert all(name in common_levels for name in df2.index.names)

    iter_index_1 = df1.reset_index([c for c in df1.index.names if c not in common_levels]).pipe(iter_index_tuples)
    iter_index_2 = list(iter_index_tuples(df2))
    mask = [x in iter_index_2 for x in iter_index_1]
    return df1[mask]
    
DOLLAR = "${:,.2f}"
WHOLE = "{:,.0f}"
PCT = "{:.1%}"
DECIMAL = "{0:0.2f}"

def get_fmt_from_keyword(keyword):
    # TODO: THis still has trouble with W/PL store geo names
    """ return the correct format string from a keyword"""
    colname = copy.copy(keyword)
    # in cases like units/customer, or units per customer, select the first word
    if 'per' in colname:
        checkstr = colname.split('per')[0]
    elif '/' in colname:
        checkstr = colname.split('/')[0]
    else:
        checkstr = colname
    if any(x in checkstr.lower() for x in ['sor', 'shr', 'share', 'requirement', 'pct', 'percent', "%"]):
        return PCT
    elif any(x in checkstr.lower() for x in ['decimal', 'eq unit', 'equivalized unit']) :
        return DECIMAL
    elif any(x in checkstr.lower() for x in ['unit', 'visit', 'customer', 'index', 'count', 'cnt', 'whole']):
        return WHOLE
    elif any(x in checkstr.lower() for x in ['sales', 'spend', 'dollar', 'revenue', '$']):
        return DOLLAR
    else:
        return "{}"

def fmt_series_retail(series, keyword=None, force=True):
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
        Currently implemented keywords:
            sales
            spend
            unit
            customer
            visit
            index
            sor
            share
            requirement
            pct
            percent
        Case insensitive
        If None (default), the keyword defaults to the name of the series
    """
    colname = keyword or series.name

    if series.dtype == 'O':
        logging.debug("The series was dtype 'O', returning original series")
        return series
    elif colname is None or type(colname) is not str:
        logging.warn("The column name or keyword supplied was not a string, or was not supplied at all, returning original series")
        return series
    else:
        # in cases like units/customer, or units per customer, select the first word
        # if 'per' in colname:
        #     checkstr = colname.split('per')[0]
        # elif '/' in colname:
        #     checkstr = colname.split('/')[0]
        # else:
        #     checkstr = colname

        # if (series<=1).all():
        #     return series.map(PCT.format)
        # else:
        fmt = get_fmt_from_keyword(colname)
        if fmt != "{}":
            return series.map(fmt.format)
        else:
            if force:
                if np.issubdtype(series.dtype, np.integer):
                    return series.map(WHOLE.format)
                if np.issubdtype(series.dtype, np.float):
                    return series.map(DECIMAL.format)
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
    
    return df.reindex(pd.MultiIndex.from_tuples(list(all_idx), names=df.index.names), **kwargs)


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


def multi_groupby(df, by=None, level=None, func='sum', nafill="-", max_combos=None):
    """groups by each combination of the groupby -- each level separately
    
    Only groups levels -- not columns!

    Parameters
    ----------
    df -- dataframe or series, 
    by -- list of column names to group by, default None, if both by and level are none, then groups on all index levels
    level -- list of level names to group by, default None, if both by and level are none, then groups on all index levels 
    func -- string, function to apply to each group, only supports 'sum' and 'mean' for now
    nafill -- string, string to fill na in the returning index

    NOTE: will not work without named indexes
    Output
    ------
    dataframe

    Dataframe with the index filled with <nafill> for higher order aggregation functions

    """

    if by and level:
        raise AssertionError("Only Specify one of the paramters by= or level=")
    elif by:
        groupby=by
        kind = "by"
    elif level:
        groupby=level
        kind = "level"
    else:
        groupby = df.index.names
        kind = "level"

    #level=level or list(df.index.names)
    if max_combos is None:
        max_combos = len(groupby)
    allcombos = []
    i = 0

    cols_for_func = set(df.columns).difference(set(groupby))
    for r in xrange(1,len(groupby)+1):
        if r <= max_combos:
            for combo in itertools.combinations(groupby, r):
                group_args = {kind: combo}
                if func=='sum':
                    grouped = df.groupby(**group_args)[list(cols_for_func)].sum()
                elif func=='mean':
                    grouped = df.groupby(**group_args)[list(cols_for_func)].mean()
                else:
                    raise NotImplementedError("Only functions 'sum' and 'mean' are currently supported")
                to_append = grouped.reset_index()
                # convert the grouped variables to objects (strings)
                to_append.loc[:,combo] = to_append.loc[:,combo].astype(object)
                to_append['iteration'] = i
                allcombos.append(to_append)
                i+=1
    allcombos = pd.concat(allcombos)
    allcombos.loc[:,groupby] = allcombos.loc[:,groupby].fillna(nafill)
    return allcombos.set_index(['iteration'] + groupby)

def index_to(df, index_on, index_to, inverse=False):
    """
    df: pandas series or dataframe
    index_on: level to index on
    index_to: value of that level to index to 
    inverse=False: Get the index of index_to relative to everything else, instead of everything else relative to index_to (this internally is the reciporical)

    sort order is not preserved
    An index will be calculated for all other fields of the index, and for all columns
    """
    level_labs = list(df.index.names)
    #totest = pd.Series([1,2,3,4,5,6], pd.MultiIndex.from_product([[1,2],[1,2,3]], names=['a', 'b']), name='spend')
    if df.index.nlevels > 1:
        # multi-index case
        w = df.sort_index().unstack(index_on)
        if w.columns.nlevels > 1:
            # multiindex dataframe case
            b = w.xs(index_to, axis=1, level=-1)
        else:
            # mutliindex series case
            b = w.xs(index_to, axis=1)
        r = (w.div(b, axis=0, level=0).sort_index(axis=1).stack(dropna=False)*100.).reorder_levels(level_labs)
    else:
        # single index case (both df and series)
        r = df.div(df.xs(index_to))*100
    if inverse:
        return 100.*(1/(r/100.))
    return r

def analyze_distributions(ser, compare_level, dist_level, output_global_dist=False):
    """find the distribution of the series within <dist_level>, across the <across_level>
    
    ser: pandas series
    across_level: level for with you want to compare distributions
    dist_level: level for which you want to see the distributions
    global_dist: boolean, defaul false, do you want to include a column with the global distributions for the innermost level?

    returns: DataFrame
    """ 
    sums = ser.groupby(level=[compare_level, dist_level]).sum()
    sums.name = "distribution_sum"
    distributions = sums.groupby(level=0).apply(normalize).rename("distribution_pct")
    global_dist = sums.groupby(level=1).sum().pipe(normalize).rename("global_distribution_pct")
    #indexes = (distributions.divide(global_dist)*100).rename('index')
    # this handles categoricals

    global_dist_broadcast =  pd.Series(
        [global_dist.loc[x] for x in distributions.index.get_level_values(1)], 
        index=distributions.index
        ).rename("global_distribution_pct")
    indexes = (distributions.divide(global_dist_broadcast)*100).rename("index")
    if output_global_dist:
        to_return = pd.concat([sums, distributions, indexes, global_dist_broadcast], axis=1)
    else:
        to_return = pd.concat([sums, distributions, indexes], axis=1)

    return to_return


def group_to_other(groups, weights=None, pct=.02, other_label="other"):
    ser = weights if weights is not None else pd.Series(1, index=groups.index)
    normed = ser.groupby(groups).transform(lambda x: x.sum().astype('float32') / ser.sum().astype('float32'))
    mask = normed < pct
    groups_copy = pd.Series(groups.copy())
    groups_copy[mask.values] = other_label
    return groups_copy
