import logging
import ruamel.yaml

from config import get_config

logger = logging.getLogger(__name__)


def generate_prediction_config_file(fixed_input_values, variable_input_values, output_values):
    # generate the prediction configuration file
    output_values_enriched = []
    for output_value in output_values:
        output_values_enriched.append({"target_variable": output_value,
                                       "estimator_file": get_config("job", "prediction", "estimator_file"),
                                       # TODO: automation?
                                       "greater_is_better": get_config("job", "prediction", "greater_is_better")
                                       # TODO: automation?
                                       })
    prediction_config = {
        "fixed_values": fixed_input_values,
        "variable_values": variable_input_values,
        "estimators": output_values_enriched
    }

    # Write the prediction configuration file
    try:
        prediction_config_file = get_config("job", "prediction", "config_file")
        with open(prediction_config_file, "w") as f:
            yaml = ruamel.yaml.YAML()
            yaml.indent(sequence=4, offset=2)
            yaml.default_flow_style = False
            yaml.dump(prediction_config, f)
    except Exception as e:
        logger.error(f"Error writing prediction configuration file: {e}")
    pass
