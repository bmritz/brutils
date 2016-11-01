# Source Code for {{cookiecutter.client_codename}}  {{cookiecutter.project_name}}
# Author {{cookiecutter.author_name}}


import os
import json

JSON_CONFIG_ABSPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../CONFIG.json"))

with open(JSON_CONFIG_ABSPATH) as cfil:
    CONFIG = json.load(cfil)

# base data directory on NFS -- specified in the cookiecutter prompts
DATA_DIR_BASE = CONFIG['project_data_directory']

# CONFIGURE LOGGER
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))

# these will be subdirectories in your data directory
# INPUT is raw input -- it should be IMMUTABLE
# INTERIM is for intermediate datasets created during the project & passed from program to program
# PROCESSED is for final, client sharable files, or files that feed visualizations that ultimately are shared with client
INPUT_SUBDIR = 'raw_input'
INTERIM_SUBDIR = 'interim'
PROCESSED_SUBDIR = 'processed'

DATA_DIR_RAW = os.path.join(DATA_DIR_BASE, INPUT_SUBDIR)
DATA_DIR_PROCESSED = os.path.join(DATA_DIR_BASE, PROCESSED_SUBDIR)
DATA_DIR_INTERIM = os.path.join(DATA_DIR_BASE, INTERIM_SUBDIR)

# DATA_DIR_GIT is under source control
DATA_DIR_GIT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

# MODEL DIR is under source control as well
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))



