import sys
import logging
from typing import Optional, Union

ARG_TYPE = Optional[Union[logging.INFO.__class__, logging.DEBUG.__class__, logging.ERROR.__class__,
                    logging.CRITICAL.__class__, logging.FATAL.__class__]]


def set_logger(name: Optional[str] = __name__,
               logging_level: ARG_TYPE = logging.INFO):
    logger = logging.getLogger(name)

    stream = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    stream.setFormatter(formatter)

    logger.addHandler(stream)
    logger.setLevel(logging_level)
    return logger