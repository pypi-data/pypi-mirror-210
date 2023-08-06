"""
"""
import subprocess

from klops.config import LOGGER


def shell_executor(command: str) -> subprocess.CompletedProcess:
    """
    Command line executor wrapper.
    Args:
        command (str): The shell command string.

    Returns:
        subprocess.CompletedProcess: _description_
    """
    try:
        return subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as called_error:
        LOGGER.error(str(called_error))
    except subprocess.SubprocessError as sub_error:
        LOGGER.error(str(sub_error))
    