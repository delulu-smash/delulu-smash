from __future__ import annotations  # noqa: A005

# below allows us to use streamlit as base and we can overwrite/enhance/extend/configure/etc
# on top of the loguru library
from loguru import logger  # noqa: TID251

from ssbu.logging.util import *
from ssbu.logging.util import toggle_logger

# TODO: decide if this good idea
logger.toggle = toggle_logger
# NOTE: below if for
# best practice for packages laid out by loguru
# in https://loguru.readthedocs.io/en/stable/resources/recipes.html#configuring-loguru-to-be-used-by-a-library-or-an-application
toggle_logger(enable=False)
