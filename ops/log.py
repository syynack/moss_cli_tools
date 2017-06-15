#!/usr/bin/python

import logging

moss_logger = logging.getLogger('moss')
formatter = logging.Formatter('%(asctime)s \033[1;32m%(name)s\033[0m \033[1;34m[%(levelname)s]\033[0m %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
moss_logger.addHandler(stream_handler)


def set_verbose():
    moss_logger.setLevel(logging.DEBUG)
    
    
def verbose(message):
    moss_logger.debug(message)
    
    
def info(message):
    moss_logger.setLevel(logging.INFO)
    moss_logger.warn(message)
    
    
def warning(message):
    moss_logger.setLevel(logging.WARNING)
    moss_logger.warn(message)

    
def error(message):
    moss_logger.setLevel(logging.ERROR)
    moss_logger.error(message)
    
    
def critical(message):
    moss_logger.setLevel(logging.CRITICAL)
    moss_logger.critical(message)