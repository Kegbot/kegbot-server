import logging
import os
import shutil
import tempfile

import pytest
from django.conf import settings

logger = logging.getLogger("pykeg.test.plugin")
TEMP_DATA_DIR = None


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    global TEMP_DATA_DIR
    TEMP_DATA_DIR = tempfile.mkdtemp()
    os.environ["KEGBOT_DATA_DIR"] = TEMP_DATA_DIR
    logger.info("setting KEGBOT_DATA_DIR to {}".format(TEMP_DATA_DIR))


@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    logger.info("removing KEGBOT_DATA_DIR {}".format(TEMP_DATA_DIR))
    shutil.rmtree(TEMP_DATA_DIR)
