"""
upload_to_gd
"""
import logging, os, dill
import matplotlib.pyplot as plt
from GDMetaData import GDMetaData

GD_PATH = '/Users/britz/Graphdash'
GD_STORAGE_FOLDER = 'demo_graph_dir'

def upload_to_gd(fig, metadata, 
    gd_path=GD_PATH, gd_storage_folder=GD_STORAGE_FOLDER):
    """
    The function uploads a figure to GD with the associated metadata
    It copies the files out to the GD implementation specified by gd_path & gd_storage_folder
    Modified this from Justins to:
        take a matplotlib.Figure object and dict of metadata as inputs,
        by default write to gd_path & storage folder specified globally,
        generate random filename to save data if no filename given
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
    def full_path(fil):
        return os.path.join(gd_path, gd_storage_folder, fil)

    if not isinstance(fig, plt.Figure):
        errmsg = "parameter fig in upload_to_gd must be of class matplotlib.figure.Figure"
        logging.error(errmsg)
        raise TypeError(errmsg)

    if not isinstance(metadata, GDMetaData):
        metadata = GDMetaData(metadata)

    metadata['figure_obj'] = dill.dumps(fig)

    # save images: export is .png and name is .svg 
    # save both types per GD conventions
    fig.savefig(full_path(metadata['export']))
    fig.savefig(full_path(metadata['name']))
    
    # save data so it can be exported in browser
    metadata.conform_to_GD()
    try:
        json_data = metadata['other'].pop('data')
    except KeyError:
        print "we errored"
        logging.info("""Data was not on the metadata 
            file and will not be uploaded to GraphDash""")
        metadata.pop("file")
    else:
        with open(full_path(metadata['file']), 'w') as fil:
            fil.write(json_data)
    # save metadata
    yaml_path = full_path(metadata['other']['yaml'])
    metadata.to_yaml_file(yaml_path)