import argparse
import os
import yaml


def load_config():
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
    parser = argparse.ArgumentParser()
    for key in config.keys():
        parser.add_argument(f"--{key}", type=str, help=f"Override {key} from command line")

    args = parser.parse_args()
    for key, value in vars(args).items():
        if value is not None:
            config[key] = value

    return config
