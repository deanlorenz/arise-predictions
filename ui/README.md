# ARISE prediction UI

This UI provides consumable and efficient user-friendly fronting 
to ARISE prediction functionality. It is making use of the
`streamlit` library to execute `arise` commands and present
the outputs in convenient and friendly fashion.

![Arise UI - example](docs/arise_ui_screenshot.png)

## How to run the UI

Clone the repo and then run with:
```
cd ui
python -m pip install -r requirements.txt
streamlit run main.py
```

## How to change the configuration

Change the config.yaml file to fit your custom configuration.  
The provided version from GitHub is aligned with the demo [MLCommons](../examples/MLCommons) 
example that can be found also in arise Makefile.

## How to use the UI

For details about how to use the UI, refer to [this page](docs/how_to_use_the_ui.md)