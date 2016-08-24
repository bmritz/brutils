import logging
import p_00_setup
import time
from p_02_support import support_fxn
from p_00_setup import setup_logging

logger = setup_logging(level=logging.DEBUG)
logger.info("info msg")
logger.debug("debug msg")

time.sleep(3)

y = support_fxn(2)
