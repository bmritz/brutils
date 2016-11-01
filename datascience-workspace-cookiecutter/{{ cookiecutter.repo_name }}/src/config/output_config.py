# NOTE: The imports for this configuration file assumes that you have dslib in your python path

# If you do not have dslib in your path, please clone it from https://github.com/aunalytics/dslib.git
# and set your path using add2virtualenv /my/other/path if you are using python virtualenv or by adding 
# export PYTHONPATH="${PYTHONPATH}:/my/other/path"
# to your .bashrc

from base_config import DATA_DIR_BASE, DATA_DIR_RAW, DATA_DIR_INTERIM, DATA_DIR_PROCESSED, DATA_DIR_GIT, MODEL_DIR
import oututils
import cPickle as pkl
import logging

def ezout_csv_fctry(basedir):

    def _ezout_fxn(dat, name, output_stem=basedir, subdir="", **kwargs):
        """
        Outputs a pandas dataframe as a csv
        (default folder is: %s)

        PARAMETERS
        ----------
        dat: pandas dataframe
            dataframe to be output

        name: string
            descriptive name of the dataset -- this will be appended to program number to create the filename

        output_stem: string
            filepath to the base directory where the file should be output to

        subdir: string
            subdirectory where the file should be saved to, will be appended to output_stem using os.path.join()

        **kwargs
            keyword arguments passed to pandas.DataFrame.to_csv()
        """ % basedir
        path_fxn = oututils.au_output_path_factory(output_stem=output_stem, subdir=subdir, output_extension=".csv")
        out_filname = path_fxn(name)
        dat.to_csv(out_filname, **kwargs)
        logging.info("Pandas dataframe with shape %s output to %s" % (dat.shape, out_filname))

    return _ezout_fxn
    
def ezout_pkl_fctry(basedir):

    def _ezout_fxn(dat, name, output_stem=basedir, subdir=""):
        """
        Outputs a python object to a pkl file
        (default folder is: %s)

        PARAMETERS
        ----------
        dat: python object
            object to be output

        name: string
            descriptive name of the dataset -- this will be appended to program number to create the filename

        output_stem: string
            filepath to the base directory where the file should be output to

        subdir: string
            subdirectory where the file should be saved to, will be appended to output_stem using os.path.join()
        """ % basedir

        path_fxn = oututils.au_output_path_factory(output_stem=output_stem, subdir=subdir, output_extension=".pkl")
        out_filname = path_fxn(name)
        with open(out_filname, 'wb') as fil:
            pkl.dump(dat, fil, -1)
            logging.info("File output to %s" % out_filname)

    return _ezout_fxn

output_csv2base = ezout_csv_fctry(DATA_DIR_BASE)
output_csv2interim = ezout_csv_fctry(DATA_DIR_INTERIM)
output_csv2processed = ezout_csv_fctry(DATA_DIR_PROCESSED)
output_csv2git = ezout_csv_fctry(DATA_DIR_GIT)
output_csv2raw = ezout_csv_fctry(DATA_DIR_RAW)

output_pkl2base = ezout_pkl_fctry(DATA_DIR_BASE)
output_pkl2interim = ezout_pkl_fctry(DATA_DIR_INTERIM)
output_pkl2processed = ezout_pkl_fctry(DATA_DIR_PROCESSED)
output_pkl2git = ezout_pkl_fctry(DATA_DIR_GIT)
output_pkl2raw = ezout_pkl_fctry(DATA_DIR_RAW)
output_pkl2model = ezout_pkl_fctry(MODEL_DIR)
