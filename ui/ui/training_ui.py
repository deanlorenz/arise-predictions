import logging
from string import Template

import streamlit as st

from config import config
from tools.actuator import execute_command

logger = logging.getLogger(__name__)


class TrainingUI:
    def __init__(self):
        self.title = "ARISE predictions"

    def show(self):
        self.show_page_content()

    def show_page_content(self):
        st.markdown("""
                    # ARISE training landing page
                    
                    ## This page is used to train arise models.
                    
                    There are two phases in the training:
                    
                    1. Execute `analyze-jobs` to perform statistical analysis on the data.
                    2. Execute `auto-build-models` to search and persist the best predicting model among 
                        different linear and decision tree regressors.
                        
                    Following are two buttons that execute those processes individually. 
                    Make sure to execute both, one after the other.
                    
                    > Note: Be patient. The operations might take significant amount of time.  
                    > Note: The command templates are defined in `config.yaml` file.  
                        
                    """)

        st.button("analyze-jobs", on_click=self.on_analyze_jobs_clicked)
        st.button("auto-build-models", on_click=self.on_auto_build_models_clicked)

        if 'execution_results' in st.session_state:
            st.divider
            st.markdown("### Command output")
            st.divider
            st.markdown(st.session_state.execution_results)

    def on_analyze_jobs_clicked(self):
        logger.debug(f"on_analyze_jobs_clicked")
        command_template = Template(config["actuation_templates"]["analyze-jobs"])
        logger.debug(f"command_template: {command_template}")

        # Substitute values
        command = command_template.substitute(
            title=self.title,
            job_spec_file=config["job"]["job_spec_file"],
            input_path=config["job"]["input_path"],
            python=config["job"]["python"],
            executable=config["job"]["executable"],
            model_path=config["job"]["model_path"]
            )

        # Execute the command
        result = execute_command(command)
        logger.debug(f"on_analyze_jobs_clicked result: {result}")

        st.session_state['execution_results'] = f"""
### Execution of `analyze-jobs` is completed!  
The results are:
```{result}
```
"""

    def on_auto_build_models_clicked(self):
        logger.debug(f"on_auto_build_models_clicked")
        command_template = Template(config["actuation_templates"]["auto-build-models"])
        logger.debug(f"command_template: {command_template}")

        # Substitute values
        command = command_template.substitute(
            title=self.title,
            job_spec_file=config["job"]["job_spec_file"],
            input_path=config["job"]["input_path"],
            python=config["job"]["python"],
            executable=config["job"]["executable"],
            model_path=config["job"]["model_path"]
            )

        result = execute_command(command)
        logger.debug(f"on_auto_build_models_clicked result: {result}")

        st.session_state['execution_results'] = f"""
### Execution of `auto_build_models` is completed!  
The results are:
```{result}
```
"""


