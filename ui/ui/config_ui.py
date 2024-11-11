import logging
import os

import streamlit as st

from config import config, get_config, save_config

logger = logging.getLogger(__name__)


class ConfigUI:
    def __init__(self):
        pass

    def show(self):
        self.show_page_content()

    def show_page_content(self):

        st.markdown(f"""
                    # ARISE configuration landing page
                    """)
        st.divider
        # allows the user to configure the base path for the prediction model
        with st.form(key='config-form'):
            st.subheader("Configure the base path of the prediction model")
            st.text_input("Base path", key="base_path", value=get_config("job", "base_path"),
                          help="The base path of the application prediction model")
            st.form_submit_button("Save")
            if st.session_state.base_path != config["job"]["base_path"]:
                if not os.path.isdir(st.session_state.base_path):
                    st.error('The provided folder does not exist. Please provide a valid folder path.')
                    return

                config["job"]["base_path"] = st.session_state.base_path
                logger.info(f"Base path changed to {st.session_state.base_path}")
                # Persist the configuration
                save_config()

        st.divider
        st.divider
        st.markdown(f"""
                    ## The complete UI configuration is:  
                    """)


        st.divider
        st.json(config)
        st.divider


