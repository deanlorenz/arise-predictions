import argparse
import os
import sys

import yaml
import re

config = {"not_initialized": True}


def get_config(*keys):
    global config

    if config.get("not_initialized"):
        config = load_config()

    # go through all nested keys to find the relevant value in the dict
    result = config
    for key in keys:
        result = result.get(key)

    # Split the value to find all the tokens that start with$.
    # For each $ started token, replace with the relevant value from config
    if isinstance(result, str):
        # Combine whitespace, $, /, and \ as separators
        pattern = r'([\s#/\\][^\s#/\\]+)'
        tokens = re.split(pattern, result)
        for i in range(len(tokens)):
            if tokens[i].startswith("#"):
                tokens[i] = get_config(*tokens[i][1:].split("."))
        result = "".join(tokens)

    return result


def save_config():
    global config

    # Save to YAML file
    yaml_file_path = "config.yaml"
    with open(yaml_file_path, "w") as yaml_file:
        yaml.dump(config, yaml_file)


def load_config():
    global config

    # Load from YAML file (the lowest priority)
    config = {}
    yaml_file_path = "config.yaml"
    if os.path.exists(yaml_file_path):
        with open(yaml_file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file) or {}

    # Override with environment variables (medium priority)
    for key in config.keys():
        env_value = os.getenv(key.upper())
        if env_value is not None:
            config[key] = env_value

    # Override with command-line arguments (the highest priority)
    if len(sys.argv) > 2:
        print("Command line arguments: ", sys.argv)
        parser = argparse.ArgumentParser()
        for key in config.keys():
            parser.add_argument(f"--{key}", type=str, help=f"Override {key} from command line")

        args = parser.parse_args()
        for key, value in vars(args).items():
            if value is not None:
                config[key] = value

    return config
