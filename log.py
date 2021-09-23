import logging
import sys

# set up logging
log = logging.getLogger("egg_logger")
file_handler = logging.FileHandler(filename="log.log")
file_formatter = logging.Formatter("[%(levelname)s][%(asctime)s][%(filename)s, %(funcName)s, %(lineno)d] %(message)s")
file_handler.setFormatter(file_formatter)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_formatter = logging.Formatter("%(message)s")
stdout_handler.setFormatter(stdout_formatter)
log.addHandler(file_handler)
log.addHandler(stdout_handler)
log.setLevel(logging.DEBUG)
