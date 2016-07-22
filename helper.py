"""
helper.py
Created: 2015-07-08
Brian Ritz

Contains helper functions useful with pandas
"""

import logging
import pandas as pd
import numpy as np

def printall(dat):
    """prints entire object and returns to original context"""
    with pd.option_context('display.max_rows', 999):
            print dat

def norm_horz(df):
    assert np.all(df>=0), "DataFrame input into norm_horz must have all elements >=0"
    return df.div(df.sum(axis=1), axis=0)

def norm_vert(df):
    assert np.all(df>=0), "DataFrame input into norm_vert must have all elements >=0"
    return df.div(df.sum(axis=0), axis=1)


