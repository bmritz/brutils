import os
import sys
import logging
import time, datetime
import pwd
from git import Repo, InvalidGitRepositoryError

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.isdir(d):
        os.makedirs(d)

def file_in_dir(fil, directory):
    return fil in os.listdir(directory)

def up_one_level(from_dir):
    next_dir = os.path.abspath(os.path.join(from_dir, '..'))
    return next_dir

def find_repo_root(d):
    f = '.git'
    if file_in_dir(f, d):
        return d
    elif d == "/":
        return None
    else:
        return find_repo_root(up_one_level(d))


def setup_logging(filename=None, level=logging.INFO, logging_directory = "./logs", make_file=True):
    # sys.argv will be '' if running interactively in python
    # sys.argv will be "<somedirectory>/ipython" if running interactively in ipython
    cmand = sys.argv[0].split("/")
    check1 = cmand[-1] not in ['ipython', '']
    check2 = 'ipykernel' not in cmand
    if filename or (check1 and check2):
        print("logging directory is %s" % logging_directory)
        print_to_log = True
        log_file = filename or os.path.abspath(os.path.join(logging_directory, "%s_%s.log" %
                    (os.path.split(os.path.splitext(sys.argv[0])[0])[-1], time.strftime('%Y%m%d_%H%M%S'))))
    else:
        print_to_log = False
    fmt_string = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    #repo_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    repo_dir = find_repo_root(os.path.dirname(os.path.abspath(sys.argv[0])))
    if print_to_log and make_file:
        ensure_dir(log_file)
        with open(log_file, 'w') as f:
            f.write("***AU LOGGING***\n")
            f.write("SCRIPT INFO:\n")
            f.write("Script full path: %s\n" % os.path.abspath(sys.argv[0]))
            if repo_dir is not None:
                f.write("Script Git Commit hash: %s\n" % Repo(repo_dir).head.commit.hexsha)
            else:
                f.write("Script was not in a git repository, no version info available.\n")
            f.write("Script start time: %s\n" % datetime.datetime.now())
            f.write("Script called by user: %s\n" % pwd.getpwuid(os.getuid()).pw_name)
            # TODO: add in AU command line functionality here
            if len(sys.argv) > 1:
                f.write("Command line arguments from sys.argv:")
                for cmdarg in sys.argv[1:]:
                    f.write("\t%s" % cmdarg)
            else:
                f.write("Script called with no command line arguments.")
            f.write("\n\nSCRIPT LOG:\n")
        # with open(sys.argv[0], 'rb') as orig_fil:
        #     for line in orig_fil:
        #         print line
        logging.basicConfig(filename=log_file, level=level, format=fmt_string)
        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(level)
        # set a format which is simpler
        formatter = logging.Formatter(fmt_string)
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
    else:
        logging.basicConfig(level=level, format=fmt_string)

    # set up sys.excepthook to catch an unhandled exception to the log
    def _exception_hook(exc_type, exc_value, exc_traceback):
        logging.error("Uncaught Exception!", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _exception_hook
    return logging.getLogger('')
#setup_logging()

def setup_logger(filename=None, level=logging.INFO, name=os.path.splitext(sys.argv[0])[0]):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
