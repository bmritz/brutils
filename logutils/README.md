# AU LOGGING

Create logs for your project using:
```python
import sys
sys.path.append("/path/to/brutils")
from br_logging import setup_logging
logger = setup_logging()
logger.debug("This message is NOT written to the log because the default level is logging.INFO")
logger.info("This message is written to the log")
logger.warning("This message is also written to the log")
logger.error("This message is also written to the log")
logger.critical("This message is also written to the log")
```

### Where are the logs written?
* By default, setup_logging() will create a sub-directory named logs/ in the folder of the parent program which was called at the command line
* By default, each run of the script will create a new file in the logs/ sub-directory with the naming convention **\<name of python script\>_\<YearMonthDay_HourMinuteSecond\>.log**
* You can also choose a custom filepath and filename to write the log to as a parameter to setup_logging():
```python
from br_logging import setup_logging
logger = setup_logging(filename="/path/to/logfile/logfile.log")
```
     
### What is written to the log?
* By default, the log writes the following information to the top of the log:
    * The full path of the called python script
    * The Git commit hash if the script is in a git repo
    * The date and time the script was run
    * The user who called the python command to execute the script
    * Any command line arguments that were passed with the python command to sys.argv
* You can also write any custom logging messages by passing strings the logger returned by setup_logging(). For more detail, see the docs for python's [logging facility](https://docs.python.org/2/library/logging.html#logger).

### What parameters can be passed to setup_logging()?
* ```filename=None:``` Name of the log file created. If this is set to ```None``` then the filename will be **\<name of python script\>_\<YearMonthDay_HourMinuteSecond\>.log** and will be placed in the directory specified by ```logging_directory```.
* ```level=logging.INFO```: Lowest level of messages that will be written to the log, any message passed to the logging facility that is of higher level will be written
* ```logging_directory="./logs"```: Directory where the log file will be created if ```filename=None```, if the directory does not exist, it will be created. If ```filename``` is not ```None```, then this parameter is ignored.

### What packages are needed to run au_logging?
* au_logging uses the following standard python modules:
    * os
    * sys
    * logging
    * time
    * datetime
    * pwd
* au_logging also uses the following python package:
    * [gitpython](https://gitpython.readthedocs.io/en/stable/intro.html) 

You can install all packages needed by the following command:
```sh
pip install -r requirements.txt
```
