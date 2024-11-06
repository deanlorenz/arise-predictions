from config import config
from tools.data_execution_metadata import DataExecutionMetadata
from ui.predict_ui import PredictUI

# Show the UI
data_execution_metadata_file = DataExecutionMetadata(config["job"]["data_execution_metadata_file"])

gui = PredictUI()
gui.set_input_fields(data_execution_metadata_file.job_metadata_inputs,
                     data_execution_metadata_file.job_metadata_inputs_details)

gui.set_output_fields(data_execution_metadata_file.job_metadata_outputs)

# Show the UI
gui.show()

