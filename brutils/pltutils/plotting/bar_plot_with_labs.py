import matplotlib.pyplot as plt
import au_pyutils.pdutils as pdu
import pandas as pd
import numpy as np

# plotting functions
from textwrap import wrap
def wrap_tick_labels(ax, axis='x', wraplen=30):
    if axis=='x':
        labels = ax.get_xticklabels()
        labels = [ '\n'.join(wrap(lab.get_text(), wraplen)) for lab in labels ]
        ax.set_xticklabels(labels)
    elif axis=='y':
        labels = ax.get_yticklabels()
        labels = [ '\n'.join(wrap(lab, wraplen)) for lab in labels ]
        ax.set_yticklabels(labels)
    #return ax

def get_width_height(text_object):
    r=text_object.get_figure().canvas.get_renderer()
    bb=text_object.get_window_extent(renderer=r)
    w = bb.width
    h = bb.height
    return w, h

def rotate_tick_labels(ax, rotation=45, axis='x'):

    if axis=='x':
        # re-adjust the position to get point at the center of wher it started
        labs = ax.xaxis.get_majorticklabels()
        for t in labs:
            w, h = get_width_height(t)
            x_offset = np.cos(np.deg2rad(rotation)) * (float(w)/2)
            if np.sin(np.deg2rad(rotation)) > 0:
                x_offset = -x_offset
            t.set_position((t.get_position()[0]+x_offset, t.get_position()[1]))
        ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=rotation)
    elif axis=='y':
        ax.set_yticklabels(ax.yaxis.get_majorticklabels(), rotation=rotation)        
    else:
        raise TypeError
    #return ax

def format_plot_axes(ax, fmt="{:.0}", axis='y'):
    if axis=='x':
        xlabels = ax.get_xticks()
        xlabels = [fmt.format(label) for label in xlabels]
        ax.set_xticklabels(xlabels)
    if axis == 'y':
        ylabels = ax.get_yticks()
        ylabels = [fmt.format(label) for label in ylabels ]
        ax.set_yticklabels(ylabels)        
    #return ax

def bar_plot_with_labs(ser, data_labels='value', baseline=0,
                       wraplen=20, axis_fmt=pdu.WHOLE, **kwargs):
    fig, ax = plt.subplots()
    n = ser.name
    offset = int(ser.mean()*0.02)
    fmt = pdu.get_fmt_from_keyword(n)
    if fmt == "{}":
        if np.issubdtype(ser.dtype, np.integer):
            n = "whole"
            fmt = pdu.get_fmt_from_keyword(n)
        elif np.issubdtype(ser.dtype, np.float):
            n = "decimal"
            fmt = pdu.get_fmt_from_keyword(n)
            
    
    #ser = ser.copy()
    while ser.index.nlevels > 1:
        inx_order = [x[:-1] for x in ser.index.values]
        newcol_order = [x[-1] for x in ser.index.values]
        
        #NOTE TODO: THIS WILL BREAK IF NLEVELS>2
        inx_order = pd.Series([x[0] for x in inx_order]).unique()
        newcol_order = pd.Series(newcol_order).unique()
        ser = ser.unstack(-1)
        ser = ser.loc[inx_order,newcol_order]
    (ser-baseline).plot(kind='bar', bottom=baseline, ax=ax, **kwargs)
    
    if 'value' in data_labels:
        for rect, label in zip(ax.patches, pd.DataFrame(ser).apply(pdu.fmt_series_retail, keyword = n, force=True).values.T.ravel()):
            #height = baseline + rect.get_height()
            ((x1, y1), (x2, y2)) = rect.get_bbox().get_points()
            height = ((y2 - baseline) + y1)
            
            if y1 >= baseline*.99999:
                offset_v = offset
                valign = 'bottom'
            else:
                offset_v = -offset
                valign = 'top'
                
            ax.text(rect.get_x() + rect.get_width()/2, height + offset_v, label, ha='center', va=valign)

    # y axis format
    format_plot_axes(ax, axis='y', fmt=axis_fmt)
    rotate_tick_labels(ax, axis='x', rotation=0)
    wrap_tick_labels(ax, wraplen=wraplen)
    return fig
