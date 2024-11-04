# ARIZE prediction UI

This UI provides consumable and efficient user-friendly fronting 
to ARIZE prediction functionality. It is making use of the
`streamlit` library to execute `arise` commands and present
the outputs in convenient and friendly fashion.


## How to run the UI

Clone the repo and then run with:
```
cd ui
python -m pip install -r requirements.txt
streamlit run main.py
```

## How to change the configuration

Change the config.yaml file to fit your custom configuration.  
The provided version from github is aligned with the demo mlcommon
example that can be found also in arise Makefile.