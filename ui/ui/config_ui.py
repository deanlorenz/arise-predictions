import json
import logging
from string import Template

import streamlit as st

from config import config
from tools.actuator import execute_command
from config import config

logger = logging.getLogger(__name__)


class ConfigUI:
    def __init__(self):
        pass

    def show(self):
        self.show_page_content()

    def show_page_content(self):

        st.markdown(f"""
                    # ARISE configuration landing page
                    
                    ## The UI configuration is:  
                    """)
        st.divider
        st.json(config)
        st.divider


