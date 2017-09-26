"""
This module steamlines getting the correct filenames for outputting data to a persistent file
"""

import logging
import os
import json
import re
import sys

def ensure_filepath(filepath):
    """
    Input is a filepath, not a directory
    """
    d = os.path.dirname(os.path.abspath(filepath))
    if not os.path.isdir(d):
        logging.info("The directory %s does not exist, and will be created" % d)
        os.makedirs(d)

def get_scriptname():
    """
    get the lowest level name of the script that was called with python
    """
    called_script = sys.argv[0]
    return os.path.basename(called_script)

def valid_scriptname(scriptname):
    """
    return True if the scriptname is of correct form
    """
    if re.match("^[pP]_[0-9]+_.*", scriptname):
        return True
    else:
        return False

def get_prog_numbers(scriptname):
    """
    return the numbers of the called program if it is a valid scriptname
    """
    regex_pattern = "^[pP]_[0-9]+_"
    p_and_num = re.findall(regex_pattern, scriptname)[0]
    num = p_and_num[2:-1]
    return num

def output_prefix(prefix='out_'):
    """
    This returns the output prefix appropriate for the script
    """
    sname = get_scriptname()
    if valid_scriptname(sname):
        prog_num = get_prog_numbers(sname)
        output_pref = '%s%s_' % (prefix, prog_num)
        return output_pref
    else:
        return prefix

def output_abspath(filename, output_stem=".", output_extension='', file_prefix='', subdir=''):
        """
        Inputs:
            filename: The informational name of the file to be written to. A prefix & suffix may be added..
            output_stem: the stem of the output directory
            output_extension: the file extension of the output
            file_prefix: The prefix to the filename, usually related to the name of the script
        Outputs:
            A full path to the output file: <output_stem>/<output_prefix><nickname><output_extension>
        """
        stem_abspath = os.path.abspath(output_stem)
        full_filename = file_prefix+filename+output_extension
        full_path = os.path.join(stem_abspath, subdir, full_filename)
        ensure_filepath(full_path)
        logging.info("The output path is: %s" % full_path)
        return full_path

def au_output_path_factory(output_stem='.', output_extension='.json', subdir=""):
    """
    This outputs a function that can be called to return the full path to be output to
    This will also ensure that the output directory exists, so you can write to the file
    """
    ensure_filepath(os.path.join(output_stem, 'dummy_file_not_created.txt'))
    output_pref = output_prefix()
    logging.debug("A function was created to output to %s with prefix %s and extension %s as the default" % (output_stem, output_pref, output_extension))
    def _output_abspath(filename, subdir=subdir, output_stem=output_stem, output_extension=output_extension, file_prefix=output_pref):
        """
        Inputs:
            filename: The informational name of the file to be written to. A prefix & suffix may be added..
        Outputs:
            A full path to the output file: <stem>/<output_prefix><prog_num><nickname><output_extension>
        """
        full_path = output_abspath(filename, subdir=subdir, output_stem=output_stem, output_extension=output_extension, file_prefix=file_prefix)
        return full_path

    return _output_abspath
