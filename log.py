import logging
import sys

# set up logging
log = logging.getLogger("egg_logger")
formatter = logging.Formatter("[%(levelname)s][%(asctime)s][%(filename)s, %(funcName)s, %(lineno)d] %(message)s")
file_handler = logging.FileHandler(filename="log.log")
file_handler.setFormatter(formatter)
stdout_handler = logging.StreamHandler(sys.stdout))
stdout_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(stdout_handler)
log.setLevel(logging.DEBUG)
