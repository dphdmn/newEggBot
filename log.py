import logging
import sys

# set up logging
log = logging.getLogger("egg_logger")
log.addHandler(logging.FileHandler(filename="log.log"))
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)
