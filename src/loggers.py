# coding: utf-8

import logging
import os


logger = logging.getLogger("cp")
logger.addHandler(logging.StreamHandler())
server_logger = logging.getLogger("cp.server")
client_logger = logging.getLogger("cp.client")

if os.environ.get("DEBUG") is None:
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.DEBUG)
