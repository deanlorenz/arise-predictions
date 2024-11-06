import logging
import os

import streamlit as st

from config import load_config
from config import config

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

    # delete prediction files if exists
    if os.path.exists(config["job"]["prediction"]["all_predictions_file"]):
        os.remove(config["job"]["prediction"]["all_predictions_file"])
    if os.path.exists(config["job"]["prediction"]["predictions_with_ground_truth_file"]):
        os.remove(config["job"]["prediction"]["predictions_with_ground_truth_file"])

    logger.debug(f"Config: {config}")
    st.markdown(f"""

# :sparkles: Welcome to ARISE :sparkles:
## AI Right Sizing Engine

---

AI Right Sizing Engine (ARISE) is a tool for predicting required resources and execution time of an AI workload, based 
on historical executions or performance benchmarks of similar workloads (a workload dataset). ARISE is intended to 
support configuration decision-making for platform engineers or data scientists operating with AI stacks.

---


## :arrow_left: Usage: 

Use the left navigation bar to navigate 
through the pages of the application.

""")
