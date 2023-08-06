import logging

from .regex import RE_DATASETS
from .utils import execute

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

def get_datasets(pool):
    command = ["zdb", "-P", "-d", pool]
    result = execute(command)

    if "zdb: can't open" in result.stderr:
        # Check for exported pool
        command.insert(1, "-e")
        result = execute(command)

    # Parse datasets
    datasets = [m.groupdict() for m in RE_DATASETS.finditer(result.stdout)]
    logger.debug(datasets)

    return datasets
