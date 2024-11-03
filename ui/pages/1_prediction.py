from config import config
from tools.job_spec import JobSpec
from ui.predict_ui import PredictUI

# Show the UI
job_spec = JobSpec(config["job"]["job_spec_file"])

gui = PredictUI()
gui.set_input_fields(job_spec.job_metadata_inputs)
gui.set_output_fields(job_spec.job_metadata_outputs)

# Show the UI
gui.show()
