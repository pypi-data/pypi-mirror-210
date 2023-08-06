from .monitoring import Client
from . import (
    markdown,
    params
)

import logging


def logger(verbose: bool = False) -> None:
    logger = logging.getLogger('minecraftmonitoring')
    logger.setLevel(logging.DEBUG)

    if verbose:
        formatter = logging.Formatter('[%(funcName)s] %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

__author__ = 'Xpos587'