from base_config import DATA_DIR_BASE, DATA_DIR_RAW, DATA_DIR_PROCESSED, \
         DATA_DIR_INTERIM, DATA_DIR_GIT, JSON_CONFIG_ABSPATH, MODEL_DIR

from output_config import output_csv2base, output_csv2interim, output_csv2processed, output_csv2git, output_csv2raw, \
         output_pkl2base, output_pkl2interim, output_pkl2processed, output_pkl2git, output_pkl2raw, output_pkl2model

from log_config import LOG

import json

with open(JSON_CONFIG_ABSPATH) as cfil:
    CONFIG = json.load(cfil)
