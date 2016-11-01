# NOTE: The imports for this configuration file assumes that you have dslib in your python path

# If you do not have dslib in your path, please clone it from https://github.com/aunalytics/dslib.git
# and set your path using add2virtualenv /my/other/path if you are using python virtualenv or by adding 
# export PYTHONPATH="${PYTHONPATH}:/my/other/path"
# to your .bashrc

from base_config import LOG_DIR
from logutils import setup_logging
import logging, types

LOG = setup_logging(level=logging.INFO, logging_directory=LOG_DIR)

def log_shape(self, df, id):
    self.info("The shape of the dataframe %s is %s" % (id, str(df.shape)))

def log_cols(self, df, id):
    self.info("The columns of the dataframe %s are: %s" % (id, str(df.columns)))

def log_value(self, var, id):
    self.info("The value of the variable %s is: %s" % (id, str(var)))

LOG.log_value = types.MethodType(log_value, LOG)
LOG.log_cols = types.MethodType(log_cols, LOG)
LOG.log_shape = types.MethodType(log_shape, LOG)
