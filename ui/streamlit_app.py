import logging

from config import load_config
from config import config
from tools.job_spec import JobSpec
from ui.predict_ui import PredictUI

logger = logging.getLogger(__name__)


def init_logging():
    global logger

    if config.get("loglevel") is None:
        config["loglevel"] = "INFO"

    # Setting log level
    level = logging.getLevelName(config["loglevel"].upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)


if __name__ == "__main__":
    config = load_config()
    init_logging()

    logger.debug(f"Config: {config}")

    # Parse the job_spec file
    job_spec = JobSpec(config["job"]["job_spec_file"])

    # Build the UI
    gui = PredictUI()
    gui.set_input_fields(job_spec.job_metadata_inputs)
    gui.set_output_fields(job_spec.job_metadata_outputs)

    # Show the UI
    gui.show()

