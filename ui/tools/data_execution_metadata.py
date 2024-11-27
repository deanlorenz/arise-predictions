import os
import yaml


class DataExecutionMetadata:

    def __init__(self, data_execution_metadata_file):
        # check that data_execution_metadata_file is not None
        if data_execution_metadata_file is None:
            raise ValueError("data_execution_metadata_file file is required")
        # check that the file exists
        if not os.path.exists(data_execution_metadata_file):
            raise ValueError(f"data_execution_metadata_file file {data_execution_metadata_file} does not exist")

        self.data_execution_metadata_file = data_execution_metadata_file
        self.job_metadata_inputs = []
        self.job_metadata_inputs_details = {}
        self.job_metadata_outputs = []
        self.job_metadata_costs = {}
        self.parse()

    def parse(self):
        # parse the data_execution_metadata_file
        with open(self.data_execution_metadata_file, 'r') as file:
            content = yaml.safe_load(file)
            if content is None:
                raise ValueError(f"data_execution_metadata file "
                                 f"{self.data_execution_metadata_file} is empty")
            if "inputs" not in content:
                raise ValueError(f"data_execution_metadata file "
                                 f"{self.data_execution_metadata_file} does not contain inputs")
            if "outputs" not in content:
                raise ValueError(f"data_execution_metadata file "
                                 f"{self.data_execution_metadata_file} does not contain outputs")

            if "costs" not in content:
                raise ValueError(f"data_execution_metadata file "
                                 f"{self.data_execution_metadata_file} does not contain costs")

            self.job_metadata_inputs = content["inputs"]
            self.job_metadata_outputs = content["outputs"]
            self.job_metadata_costs = content["costs"]

            # get output details
            for _input in self.job_metadata_inputs:
                if _input not in content:
                    raise ValueError(
                        f"data_execution_metadata file "
                        f"{self.data_execution_metadata_file} does not contain details for {_input} input")
                self.job_metadata_inputs_details[_input] = content[_input]

            # validate cost params
            valid_params = set(self.job_metadata_inputs) | set(self.job_metadata_outputs)
            for _param in ['count', 'unit', 'denominator']:
                if self.job_metadata_costs.get(_param, None) not in valid_params:
                    raise ValueError(
                        f"data_execution_metadata file "
                        f"{self.data_execution_metadata_file} does not contain cost param {_param}")
