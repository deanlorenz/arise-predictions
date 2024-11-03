import subprocess
import logging

logger = logging.getLogger(__name__)


def execute_command(command):
    try:
        # Run each command and capture output
        command_result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        result = (f"Command succeeded: {command}  \n"
                  f"Output:\n{command_result.stdout.strip()}  \n")
        logger.info(result)
    except Exception as e:
        # error handling
        result = (f"Command failed: {command}  \n"
                  f"Error:\n{e.stderr.strip()}  \n")
        logger.error(result)

    return result
