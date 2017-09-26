import os, pwd
import pandas as pd
import datetime
import numpy as np
import dill, inspect
import matplotlib.pyplot as plt
import matplotlib
from upload_to_gd import upload_to_gd, GDMetaData, GD_PATH, GD_STORAGE_FOLDER

matplotlib.interactive(False)

def data_ingest(data):
    """
    currently not used
    could use this to ingest either a dataframe or json dynamically
    """
    if isinstance(data, pd.DataFrame):
        return data.to_json(), data
    elif isinstance(data, str):
        return data, pd.read_json(data)


class GDPlot(object):
    """
    A plot object that can be uploaded to graphdash or shown in the interpreter
    data must be a pandas dataframe with at least 1 column named "value"
    style must be of a common format (to be determined later)
    plot_fxn must be a function of inputs pd.DataFrame, style, and output a matplotlib figure
    """
    def __init__(self, data_frame, style, plot_fxn, metadata={}, **kwargs):
        """ 
        TODO(MAYBE):
            MIGHT HAVE TO CHANGE style Keyword to another word to avoid collisions
        data_frame should only be indexed BY POSITION when using the plot_fxn
            -so we can change column names and have the changes flow through to the plot
        
        style is not implemented yet -- may not need to be because we save the actual figure
        
        plot_fxn should take as input data and style
            plot function should only reference colsthe data_frame by POSITION

        metadata should be a dict:
            {
            title: title of the graph, recommended for display purposes (string; markdown syntax)
            family: the subsection in which the graph is (string or list of strings for sub-categories)
            index: an optional list of keyword strings describing the graph (useful for search feature)
            text: an optional description of the graph (string; markdown syntax)
            rank: integer, optional value used to change graphs order (default uses titles)
            labels: a list of label strings (like 'new') which will be rendered in the UI as colored circles
            other keys: other metadata not used by GraphDash, 
                        but may be needed by other things reading the metadata
                        These will be entered into the graphdash api under ['other']['subkey']
            }
        """
        auto_metadata = {
        'created': str(datetime.datetime.now()),
        'function': dill.dumps(plot_fxn),
        'user': pwd.getpwuid(os.getuid()).pw_name
        }

        self.metadata = GDMetaData(auto_metadata)

        self.metadata['other']['plot_fxn_kwargs'] = kwargs
        
        if "function_source" not in metadata:
            if "other" not in metadata:
                try:
                    self.metadata['other']['function_source'] = inspect.getsource(plot_fxn)
                except IOError:
                    logging.warn("Function source could not be loaded.")
                    # maybe append the IOError on here

        style = style or matplotlib.rcParams

        # update will create attributes data_frame, style, fig, and plot_fxn
        self.update(data_frame=data_frame, style=style, 
            plot_fxn=plot_fxn, metadata=metadata)

    def show(self):
        self.fig.show()

    def get_function_source(self):
        try:
            return inspect.getsource(self.plot_fxn)
        except IOError:
            try:
                return self.metadata["function_source"]
            except KeyError:
                try:
                    return self.metadata['other']['function_source']
                except KeyError:
                    return "No Function Source Code Available"

    def get_new_uuid(self):
        new_uid = self.metadata.get_new_uuid()
        return new_uid

    def write_data(self, file):
        """csv writing untested -- may print long string"""
        filename, file_extension = os.path.splitext(file)
        with open(file, 'w') as fil:
            if file_extension == '.json':
                fil.write(self.data_json)
            elif file_extension == '.csv':
                fil.write(self.data_frame.to_csv())

    def update(self, data_frame=None, style=None, plot_fxn=None, metadata=None):
        """
        update the plot
        """
        update_fig = False
        if metadata is not None:
            self.metadata.update(metadata)
        if data_frame is not None:
            self.data_frame = data_frame
            # need orient=split to preserve ordering,
            # otherwise pd.read_json changes the order of rows for some reason
            # self.data_json = data_frame.to_json(orient="split")
            self.metadata['other'].update({"data":self.data_frame.to_json(orient="records")})
            update_fig=True
        if style is not None:
            self.style = style
            update_fig = True
        if plot_fxn is not None:
            self.plot_fxn = plot_fxn
            self.exact_plot_fxn = lambda data_frame: self.plot_fxn(data_frame, **self.metadata.recurse_get('plot_fxn_kwargs', {}))
            self.metadata['other'].update({"function":dill.dumps(plot_fxn), "function_source":self.get_function_source()})
            update_fig = True
        if update_fig:
            with plt.style.context((self.style)):
                self.fig = self.exact_plot_fxn(self.data_frame);

    def to_graphdash(self, metadata={}):
        """
        Upload the plot to graphdash 
        with the option to update associated metadata
        """
        self.update(metadata=metadata)
        self.metadata.conform_to_GD()
        self.metadata.GD_standard_text() 

        upload_to_gd(self.fig, self.metadata)




