import matplotlib.pyplot as plt

def sector_plot(df):
    """Creates sector plot (quadrant plot)
    
    Divides the plot space into equally large rectangles 
    and places text of metrics in those rectangles. Dynamically
    creates as many rectangles as the data calls for. 
    
    Args:
        df: Pandas DataFrame, multi-indexed with 2-levels with at least one named column
            The first index name will be the name of the X-axis, 
            The second index name will be the name of the Y-axis
            
            The level values of the indicies will be the labels for each sector
                You may have more than 2 level values for each index=
                Order will be preserved --
                    The first value for each level will be closest to the origin,
            
            The names of the columns will be written inside each sector 
                next to the value of that column for that sector
                
            Multiple columns will put text for multiple metrics in the same sector

    Returns:
        A matplotlib figure representing the sector plot
    """
    x_axis_lab, y_axis_lab = df.index.names 

    x_labs = df.index.get_level_values(x_axis_lab).unique()
    y_labs = df.index.get_level_values(y_axis_lab).unique()

    num_x = len(x_labs)
    num_y = len(y_labs)

    fig = plt.figure();
    ax = fig.add_subplot(1, 1, 1);

    # make the grid
    _dummy = ax.set_xlim([0,num_x]); 
    _dummy = ax.set_ylim([0,num_y]);

    for x in range(1, num_x):
        _dummy = ax.vlines(x, 0, num_y);

    for y in range(1, num_y):
        _dummy = ax.hlines(y, 0, num_x);

    # set the ticks
    x_ticks = []
    for x in range(1, num_x+1):
        x_ticks.append(float(x)-.5)

    y_ticks = []
    for y in range(1, num_y+1):
        y_ticks.append(float(y)-.5)


    _dummy = ax.xaxis.set_tick_params(bottom="off", top="off", right="off", left="off");
    _dummy = ax.xaxis.set_ticks(x_ticks);
    _dummy = ax.xaxis.set_ticklabels(x_labs);
    _dummy = ax.set_xlabel(x_axis_lab);

    _dummy = ax.yaxis.set_tick_params(bottom="off", top="off", right="off", left="off");
    _dummy = ax.yaxis.set_ticks(y_ticks);
    _dummy = ax.yaxis.set_ticklabels(y_labs);
    _dummy = ax.set_ylabel(y_axis_lab);

    for row in df.iterrows():

        row_id_x, row_id_y = row[0]

        pos_x = x_ticks[list(x_labs).index(row_id_x)]
        pos_y = x_ticks[list(y_labs).index(row_id_y)]

        string = "\n".join(metric+": %s" % val for metric, val in row[1].iteritems())
        x1 = ax.text(pos_x, pos_y, string, 
                horizontalalignment='center',  verticalalignment='center');
    return fig;
