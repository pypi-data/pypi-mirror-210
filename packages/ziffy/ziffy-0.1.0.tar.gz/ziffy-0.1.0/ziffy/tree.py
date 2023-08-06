import logging
import re
import sqlite3

from regex import RE_TREE
from utils import execute

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

def update_tree(dataset):
    result = execute(f"zdb -e -P -dd {dataset}")
    logging.debug(result)

    content = re.findall(RE_TREE, result)
    logging.debug(content)


    return content
