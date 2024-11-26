import unittest
import logging
import sys
import os

import pandas as pd

from tests.utils.logger_redirector import LoggerRedirector
from utils import constants
from perform_predict.predict import (_create_input_space, _run_predictions, get_predict_config)

"""
Tests for perform_predict.predict.
"""

logger = logging.getLogger('test-logger')

logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout)


class TestPredict(unittest.TestCase):

    def setUp(self):
        # unittest has reassigned sys.stdout and sys.stderr by this point
        LoggerRedirector.redirect_loggers(fake_stdout=sys.stdout, 
                                          fake_stderr=sys.stderr) 
        
        self.resources_path = "tests/resources"
        self.metadata_path = "tests/resources"
        self.predict_config_file = os.path.join(self.resources_path, 
                                              "example-demo-mlcommons-config.yaml")
        self.script_dir = os.path.dirname(__file__)
        self.output_path = os.path.abspath(os.path.join(
               self.script_dir, "test-tmp", constants.PRED_OUTPUT_PATH_SUFFIX))
        self.input_space_df_file = "input-space.csv"

        self.predictions_thpt_file = "predictions-tokens_per_second.csv"
        self.predictions_all_file = constants.PRED_ALL_PREDICTIONS_FILE

        self.data_execution_history_file = "mlcommons_inference_data_execution_history.csv"
    
    def tearDown(self):
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr)
    
        # if os.path.exists(self.output_path):
        #     shutil.rmtree(self.output_path)

    def test_read_input_config_values(self):
        """
        Reads input feature space configuration as expected.
        """
        input_config = get_predict_config(self.predict_config_file)
        logger.info(f"fixed_values {input_config.fixed_values}")
        logger.info(f"variable_values {input_config.variable_values}")
        self.assertIsNotNone(input_config.fixed_values)
        self.assertIsNotNone(input_config.variable_values)
        self.assertEqual(7, len(input_config.fixed_values))
        self.assertEqual(3, len(input_config.variable_values))

    def test_create_input_space(self):
        """
        DataFrame representing input space is created.
        """
        input_config = get_predict_config(self.predict_config_file)
        original_data_df = pd.read_csv(os.path.join(
            self.resources_path,
            self.data_execution_history_file))
        path, _ = _create_input_space(input_config,  original_data_df, self.output_path)
        self.assertEqual(path, os.path.join(
            self.output_path,
            self.input_space_df_file
        ))
        self.assertTrue(os.path.exists(path))

    def test_read_estimator_config(self):
        """
        Reads estimator configuration for each target variable.
        """
        estimator_config = get_predict_config(self.predict_config_file)
        logger.info(f"estimator_config: {estimator_config}")
        self.assertTrue(2, len(estimator_config.estimators))

    def test_predictions_exist(self):
        """
        Running predictions produces CSV files as expected.

        Note that we are using an input space generated from inference latency
        data using the test functions above and estimator binaries created by
        auto-model build on the same data.
        """
        config = get_predict_config(self.predict_config_file)
        original_data_df = pd.read_csv(os.path.join(
            self.resources_path, 
            self.data_execution_history_file))

        _, input_space_df = _create_input_space(
            input_config=config,
            original_data= original_data_df,
            metadata_path=self.metadata_path,
            feature_engineering=None,
            output_path=self.output_path
        ) 
        
        _run_predictions(
            original_data=original_data_df,
            input_data=input_space_df,
            estimators_config=config.estimators,
            estimator_path=self.resources_path,
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.predictions_thpt_file)))
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.predictions_all_file)))
        predictions_all_df = pd.read_csv(os.path.join(
            self.output_path, self.predictions_all_file
        ))
        self.assertIn("rank_tokens_per_second", predictions_all_df.columns)
        