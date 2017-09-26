import os, yaml, logging, json
import dill
import pandas as pd
from GDMetaData import GDMetaData
from au_plot import GDPlot
from upload_to_gd import GD_PATH, GD_STORAGE_FOLDER


def get_plot_metadata(filename, 
    gd_path = GD_PATH, 
    gd_storage_folder = GD_STORAGE_FOLDER):
    """retrieve plot metadata as a dictionary"""
    full_yaml_file = filename+".yaml"
    yamlpath = os.path.join(gd_path, gd_storage_folder, full_yaml_file)
    with open(yamlpath, "r") as yamdat:
        info = yaml.load(yamdat)
    assert isinstance(info, dict)
    return GDMetaData(info)

def get_plot_data(filename, 
    gd_path = GD_PATH, 
    gd_storage_folder = GD_STORAGE_FOLDER,
    how='df', orient="records"):
    """
    retrieve the plot data
    returns a data frame
    """
    info = get_plot_metadata(filename, 
        gd_path = gd_path, gd_storage_folder=gd_storage_folder)

    try:
        datapath = info['file']
    except KeyError:
        ermsg = "No data available for specified file."
        logging.error(ermsg)
        raise KeyError(ermsg)

    full_datapath = os.path.join(gd_path, gd_storage_folder, datapath)
    with open(full_datapath, "r") as data_json:
        jstring = json.load(data_json)
    if how == 'df':
        return pd.read_json(jstring, orient=orient)
    elif how == 'json':
        return jstring
    else:
        ermsg = "the how parameter in get_plot_data must be either 'df' or 'json'"
        logging.error(ermsg)
        raise KeyError(ermsg)


def get_plot_fxn(filename, 
    gd_path = GD_PATH, 
    gd_storage_folder = GD_STORAGE_FOLDER):
    """ 
    input the filename without extension
    returns the function that created the plot 
    from the uuid of the plot in GraphDash
    TODO: Test this -- figure a way to handle namespaces
    """
    info = get_plot_metadata(filename, 
        gd_path = gd_path, gd_storage_folder=gd_storage_folder)
    plotfunc = dill.loads(info['other']['function'])
    return plotfunc

def get_plot_fig(filename, 
    gd_path = GD_PATH, 
    gd_storage_folder = GD_STORAGE_FOLDER):
    """ 
    input the filename without extension
    returns the function that created the plot 
    from the uuid of the plot in GraphDash
    TODO: Test this -- figure a way to handle namespaces
    """
    info = get_plot_metadata(filename, 
        gd_path = gd_path, gd_storage_folder=gd_storage_folder)
    plotfig = dill.loads(info['other']['figure_object'])
    return plotfig

def get_auplot(filename, 
    gd_path = GD_PATH, 
    gd_storage_folder = GD_STORAGE_FOLDER):
    """
    This returns an AuPlot object from the GraphDash

    programming note:
        2 ways to go about this:
            re-import figure directly from dill [other][figure_obj]
            or
            apply function back to the data

    TODO: implement style -- right now it is not hooked up
    """

    def full_path(fil):
        return os.path.join(gd_path, gd_storage_folder, fil)

    metadata = get_plot_metadata(filename,
        gd_path = gd_path, gd_storage_folder = gd_storage_folder)

    if 'file' in metadata:
        dat_filename = os.path.join(gd_path, gd_storage_folder, metadata['file'])
        data = pd.read_json(dat_filename, orient="records")

    plot_fxn = dill.loads(metadata['other']['function'])

    return GDPlot(data_frame=data, plot_fxn=plot_fxn, 
        style="default_style", metadata=metadata)

