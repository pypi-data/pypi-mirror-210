import logging
import subprocess as sp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

def execute(command):
    logger.debug(command)
    result = sp.run(
        command,
        capture_output=True,
        text=True,
    )
    logger.debug(result)

    if "some devices require root privileges" in result.stderr:
        raise Exception("Root privileges required to access disks.")

    return result

def order_of_magnitude(value):
    if value >= 1e12:
        return f"{value / 1e12:.1f} T"
    elif value >= 1e9:
        return f"{value / 1e9:.1f} G"
    elif value >= 1e6:
        return f"{value / 1e6:.1f} M"
    elif value >= 1e3:
        return f"{value / 1e3:.1f} K"
    else:
        return f"{value}"
