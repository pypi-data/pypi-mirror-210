"""
This is the ss_logger module.
Here you can add a description of what your module does.
"""
__version__ = "0.2.1"

import logging
import os
from snakecase import convert
from logging.handlers import RotatingFileHandler

def get_log_file_name(class_obj_or_name):
    if isinstance(class_obj_or_name, str):
        class_name = class_obj_or_name
    else:
        class_name = class_obj_or_name.__name__
    return convert(class_name) + '.log'

def config_common_logger(filename,projectRootDirPath,log_level=logging.DEBUG, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    # Configure rotating file handler
    log_path = os.path.join(projectRootDirPath, 'logs', filename)
    max_file_size = 1000000 # 1 MB
    backup_count = 10
    rotating_handler = RotatingFileHandler(log_path, maxBytes=max_file_size, backupCount=backup_count)
    rotating_handler.setFormatter(logging.Formatter(log_format))

    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Configure logger
    logger = logging.getLogger(__name__)
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)

    return logger
