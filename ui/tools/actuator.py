import subprocess
import logging

logger = logging.getLogger(__name__)


def execute_command(original_commands):
        # Run each command and capture output
        commands = original_commands.split(";")
        result = ""
        for command in commands:
            try:
                command_result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                result += (f"Command succeeded: {command}  \n"
                          f"Output:\n{command_result.stdout.strip()}  \n")
                logger.info(result)
            except Exception as e:
                # error handling
                result += (f"Command failed: {command}  \n"
                           f"Error:\n{e}  \n")
                logger.error(result)

        return result
