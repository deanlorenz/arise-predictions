import os
import yaml


class JobSpec:
    def __init__(self, job_spec_file):
        # check that job_spec_file is not None
        if job_spec_file is None:
            raise ValueError("Job spec file is required")
        # check that the file exists
        if not os.path.exists(job_spec_file):
            raise ValueError(f"Job spec file {job_spec_file} does not exist")

        self.job_spec_file = job_spec_file
        self.job_metadata_inputs = []
        self.job_metadata_outputs = []
        self.parse()

    def parse(self):
        # parse the job_spec_file
        with open(self.job_spec_file, 'r') as file:
            content = yaml.safe_load(file)
            if content is None:
                raise ValueError(f"Job spec file {self.job_spec_file} is empty")
            if "job-metadata-inputs" not in content:
                raise ValueError(f"Job spec file {self.job_spec_file} does not contain job-metadata-inputs")
            if "job-metadata-outputs" not in content:
                raise ValueError(f"Job spec file {self.job_spec_file} does not contain job-metadata-outputs")

            self.job_metadata_inputs = content["job-metadata-inputs"]
            self.job_metadata_outputs = content["job-metadata-outputs"]
