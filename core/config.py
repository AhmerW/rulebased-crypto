from typing import Final
import logging.config
import logging
import os

from fastapi import FastAPI

ShariaCryptoCheckerAPP = FastAPI()

logging.config.fileConfig(
    os.path.join("core", "logging.conf"),
    disable_existing_loggers=False,
)
logger = logging.getLogger(__name__)
ShariaCryptoCheckerAPP.logger = logger
