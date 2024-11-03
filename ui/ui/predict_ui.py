import logging
import os
from string import Template

import pandas as pd
import streamlit as st

from tools.actuator import execute_command

logger = logging.getLogger(__name__)


# class that represents the UI and the variables associated with the ui
class PredictUI:
    def __init__(self):
        self.test = None
        self.title = "ARISE predictions"
        self.output_fields = None
        self.input_fields = None

    def set_input_fields(self, input_fields):
        self.input_fields = {}
        for input_field in input_fields:
            self.input_fields[input_field] = {"name": input_field,
                                              "placeholder": input_field,
                                              "type": "text_input"}

    def set_output_fields(self, output_fields):

        self.output_fields = {}
        for output_field in output_fields:
            self.output_fields[output_field] = {"name": output_field,
                                                "placeholder": output_field,
                                                "value": True,
                                                "type": "toggle"}

    def show(self):
        self.set_page_layout()
        self.show_page_content()
        self.show_sidebar()

    def set_page_layout(self):
        st.set_page_config(page_icon="⌛️", layout="wide", page_title="ARISE Prediction")

    def show_page_content(self):
        st.markdown("""
                    # ARISE prediction landing page

                    This page is used for predicting required resources and execution time of an AI workload, 
                    based on historical executions or performance benchmarks of similar workloads (a workload dataset)

                    ## How to use this page

                    On the sidebar
                    
                    1. Select the input values for the predictions 
                    2. Select the output values to be shown in the results
                    3. Click on the `Predict` button
                    
                    4. The results will be shown in the main page

                    > Note: Make sure to train the models before performing prediction, more info can be found on the   
                    on the training page.
                    > Note: Be patient. The operations might take some time.    
                    """)

        if 'all-predictions.csv' in st.session_state:
            st.markdown("## Prediction result")
            st.write(st.session_state['all-predictions.csv'])

        if 'predictions-with-ground-truth.csv' in st.session_state:
            st.markdown("## Ground-truth result")
            st.write(st.session_state['predictions-with-ground-truth.csv'])

        if 'prediction_results' in st.session_state:
            st.divider
            st.markdown("## Prediction command output")
            st.divider
            st.markdown(st.session_state.prediction_results)

    def add_form_element(self, element):
        if element["type"] == "text_input":
            st.text_input(element["name"], key=element["name"], placeholder=element["placeholder"])
        elif element["type"] == "toggle":
            st.toggle(element["name"], key=element["name"], value=element["value"])
        else:
            st.text(f"Unknown element type {element}")

    def show_sidebar(self):
        with (st.sidebar):
            st.header("Prediction configuration:")
            with st.form("Configuration"):
                st.subheader("Select input configuration:",
                             help="For each of the input features, select a specific value or"
                                  "use-multi selection to predict for all the values")
                for input_field_value in self.input_fields.values():
                    self.add_form_element(input_field_value)

                st.divider()
                st.subheader("Select output configuration:",
                             help="For each of the output features, select which features to present")

                for output_field_value in self.output_fields.values():
                    self.add_form_element(output_field_value)

                st.divider()

                st.form_submit_button("Predict", on_click=self.on_predict)

                st.toggle("compare with ground truth", key="compare_with_ground_truth", value=False,
                          help="Compare the results with the ground truth")

    def on_predict(self):
        from config import config

        logger.debug(f"on_predict")
        if st.session_state['compare_with_ground_truth']:
            command_template = Template(config["actuation_templates"]["demo-predict"])
        else:
            command_template = Template(config["actuation_templates"]["predict"])
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
        logger.debug(f"on_predict result: {result}")


        st.session_state['prediction_results'] = f"""
### Execution of `prediction` is completed!  
The results are:
```{result}
```
"""

        # get the prediction file if exists
        if os.path.exists("../examples/MLCommons/ARISE-predictions/all-predictions.csv"):
            csv = pd.read_csv("../examples/MLCommons/ARISE-predictions/all-predictions.csv")
            st.session_state['all-predictions.csv'] = csv

        # get the ground-truth file if exists
        if os.path.exists("../examples/MLCommons/ARISE-predictions/predictions-with-ground-truth.csv"):
            csv = pd.read_csv("../examples/MLCommons/ARISE-predictions/predictions-with-ground-truth.csv")
            st.session_state['predictions-with-ground-truth.csv'] = csv



