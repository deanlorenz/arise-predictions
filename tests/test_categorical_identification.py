import unittest
import logging
import sys
import os

import pandas as pd

from tests.utils.logger_redirector import LoggerRedirector

"""
Tests to determine which method to use for identifying categorical variables.
"""

logger = logging.getLogger('test-logger')

logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout)


class TestCatId(unittest.TestCase):

    def setUp(self):
        # unittest has reassigned sys.stdout and sys.stderr by this point
        LoggerRedirector.redirect_loggers(fake_stdout=sys.stdout, 
                                          fake_stderr=sys.stderr) 
        
        self.resources_path = "tests/resources"
        self.data_file = "mlcommons_inference_data_execution_history.csv"
        
        self.cat_vars = ['Accelerator', 'Availability', 'Model MLC', 'Organization', 'Processor', 'Scenario',
                         'System Name']

    def tearDown(self):
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr)
    
        # if os.path.exists(self.output_path):
        #     shutil.rmtree(self.output_path)
    
    def test_get_categorical_by_object_dtype(self):
        """
        Test that we identify all categorical features by 'object' dtype.
        """
        data = pd.read_csv(os.path.join(self.resources_path, self.data_file))
        categorical_by_obj = [
            cols for cols in data.columns if data[cols].dtype == 'object']
        logger.info(("categorical features by 'object' dtype:" 
                     f" {categorical_by_obj}"))
        self.assertListEqual(categorical_by_obj, self.cat_vars)

    def test_get_categorical_by_numeric_data_function(self):
        """
        Test we identify all categorival features using _get_numeric_data().
        Probably not a good idea to use a hidden function, but one of the
        recommendations on the Interwebs
        """
        data = pd.read_csv(os.path.join(self.resources_path, self.data_file))
        cols = data.columns
        num_cols = data._get_numeric_data().columns
        categorical_by_elimination = list(set(cols) - set(num_cols))
        logger.info(("categorical features by elimination:" 
                     f" {categorical_by_elimination}"))
        categorical_by_elimination.sort()
        self.assertListEqual(categorical_by_elimination, self.cat_vars)

    def test_get_categorical_by_failed_conversion_to_numeric(self):
        """
        Test that we identify all categorical features by failed ('NaN') 
        numeric conversion.

        Note this test fails as the method fails to detect one of the
        categorical variables as such (quantization mode). Can decide to negate
        the test condition to make this pass in case we run automated test
        suites at some point.
        """
        data = pd.read_csv(os.path.join(self.resources_path, self.data_file))
        categorical_by_num = []

        for column in data.columns.values.tolist():
            if pd.isna(pd.to_numeric(data[column], errors='coerce')).all():
                categorical_by_num.append(column)
        logger.info(("categorical features by conversion to numeric:" 
                     f" {categorical_by_num}"))
        self.assertListEqual(categorical_by_num, self.cat_vars)