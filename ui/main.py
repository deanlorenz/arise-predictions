import logging
import os

import streamlit as st

from utils.config import load_config, get_config
from utils.config import config

logger = logging.getLogger(__name__)


def init_logging():
    global logger

    if config.get("loglevel") is None:
        config["loglevel"] = "INFO"

    # Setting log level
    level = logging.getLevelName(get_config("loglevel").upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # Suppress logging for watchdog.observers.inotify_buffer
    logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.ERROR)


if __name__ == "__main__":

    # **** for deployment on stremlit cloud ****
    # When the app is loaded from the root folder using `steamlit run ui/main.py` command,
    # We need to change the directory to the ui directory so that the config.yaml file can be loaded correctly.
    if os.path.exists("ui/config.yaml"):
        os.chdir("ui")

    config = load_config()
    init_logging()

    # delete prediction files if exists
    if os.path.exists(get_config("job", "prediction", "all_predictions_file")):
        os.remove(get_config("job", "prediction", "all_predictions_file"))
    if os.path.exists(get_config("job", "prediction", "predictions_with_ground_truth_file")):
        os.remove(get_config("job", "prediction", "predictions_with_ground_truth_file"))

    logger.debug(f"Config: {config}")
    st.markdown(f"""

# :sparkles: Welcome to ARISE :sparkles:
## AI Right Sizing Engine

---

AI Right Sizing Engine (ARISE) is a tool for predicting required resources and execution time of an AI workload, based 
on historical executions or performance benchmarks of similar workloads (a workload dataset). ARISE is intended to 
support configuration decision-making for platform engineers or data scientists operating with AI stacks.

---

[![GitHub Repo](https://img.shields.io/badge/ARISE_GitHub-Repo-blue?logo=github)](https://github.com/arise-insights/arise-predictions)
[![Documentation](https://img.shields.io/badge/Documentation-How_to_use_the_ui-blue?logo=read-the-docs)](https://github.com/arise-insights/arise-predictions/blob/main/ui/docs/how_to_use_the_ui.md)

---

## :arrow_left: Usage: 

Use the left navigation bar to navigate 
through the pages of the application.

""")
