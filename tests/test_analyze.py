import unittest
import pandas as pd
import os
import sys
import logging
import shutil

from arise.job_statistics import (_init_args,
                                  _prepare_data,
                                  _compute_missing_data,
                                  _summarize_data,
                                  _correlate_data,
                                  _summarize_categorical_data,
                                  _plot_histograms,
                                  _plot_box_whiskers,
                                  _plot_correlations)
from arise.utils import constants
from tests.utils.logger_redirector import LoggerRedirector

"""
Tests for analyze data functionality.
"""

logger = logging.getLogger('test-logger')

logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout)


class TestAnalyzeData(unittest.TestCase):

    def setUp(self):
        # unittest has reassigned sys.stdout and sys.stderr by this point
        LoggerRedirector.redirect_loggers(fake_stdout=sys.stdout, 
                                          fake_stderr=sys.stderr)

        self.output_path = "test-tmp/data-analysis"
        self.job_id_column = "Custom_Job_Column"  # from job_spec.yaml

        self.full_row_job_name_1 = ["job-1", 50, 100, "table-1", 101]
        self.full_row_job_name_2 = ["job-1", 60, 90, "table-1", 303]
        self.full_row_job_name_3 = ["job-2", 60, 200, "table-1", 99]
        self.full_row_job_name_4 = ["job-2", 70, None, "table-3", 909]
        self.full_row_job_name_5 = ["job-2", 80, None, "table-3", 900]
        self.full_row_job_name_6 = ["job-2", 90, 300, "table-3", 919]
        self.empty_row_job_name_1 = [None, None, None, None, None]

        self.input_data_with_job_id = pd.DataFrame(
            [self.full_row_job_name_1, self.full_row_job_name_2,
                self.full_row_job_name_3, self.full_row_job_name_4,
                self.full_row_job_name_5, self.full_row_job_name_6,
                self.empty_row_job_name_1],
            columns=[
                self.job_id_column,  "Metric-1", "Metric-2", "Table", 
                "duration"])

        self.missing_values_file = "missing-values-job-2.csv"
        self.summary_file = "descriptive-stats.csv"
        self.correlation_file_csv_job_1 = "correlations-job-1.csv"
        self.correlation_file_csv_job_2 = "correlations-job-2.csv"
        self.histogram_file_job_1 = "histogram-job-1.pdf"
        self.histogram_file_job_2 = "histogram-job-2.pdf"
        self.box_file_job_1 = "box-job-1.pdf"
        self.box_file_job_2 = "box-job-2.pdf"
        self.correlation_file_job_1 = "correlation-job-1.png"
        self.correlation_file_job_2 = "correlation-job-2.png"
        self.categorical_table_metric1_file = "categorical-stats-Metric-1.csv"
        self.categorical_table_metric2_file = "categorical-stats-Metric-2.csv"
        self.categorical_table_duration_file = "categorical-stats-duration.csv"
        
        self.full_row_no_job_name_1 = [500, 100, None, 101]
        self.full_row_no_job_name_2 = [600, 200, None, 303]
        self.empty_row_no_job_name_1 = [None, None, None, None]

        self.input_data_without_job_name = pd.DataFrame(
            [self.full_row_no_job_name_1, self.full_row_no_job_name_2, 
             self.empty_row_no_job_name_1],
            columns=["Metric-1", "Metric-2", "Metric-3", "duration"])

        self.custom_job_name = "Custom_Job_Name"

    def tearDown(self):
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout, fake_stderr=sys.stderr)
        # unittest will revert sys.stdout and sys.stderr after this

        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

    # Data preparation tests
        
    def test_drops_empty_rows_and_columns(self):
        """
        All empty rows and empty columns are dropped.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id, 
            job_id_column=self.job_id_column, 
            custom_job_name=None)
        self.assertEqual(len(result_data.index), 6)
        self.assertNotIn("Aggregate", result_data.columns)
    
    def test_job_name_column_from_input_data_exists(self):
        """
        The job id column from the preprocessed input data exists in the 
        resulting DataFrame.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column, 
            custom_job_name=None)
        self.assertIn(self.job_id_column, result_data.columns)

    def test_job_name_column_is_added(self):
        """
        If no job id column exists in preprocessed data (i.e. not specified in
        job_spec.yaml) and no custom job name is specified via an argument, 
        the initialization of arguments will return the default job name column
        and default job name. prepare_data will add this column and value to 
        the data.
        """
        job_id_column, job_name = _init_args(
            job_id_column=None, 
            custom_job_name=None, 
            output_path=self.output_path)
        result_data = _prepare_data(
            data=self.input_data_without_job_name,
            job_id_column=job_id_column, 
            custom_job_name=job_name)
        self.assertIn(constants.DEFAULT_JOB_ID_COLUMN, result_data.columns)

    def test_job_name_column_with_job_name_is_added(self):
        """"
        If no job id column exists in preprocessed data (i.e. not speicified in
        job_spec.yaml), but a custom job name is specified via an argument, a
        default job name column filled with this job name will be added.
        """
        job_id_column, job_name = _init_args(
            job_id_column=None,
            custom_job_name=self.custom_job_name,
            output_path=self.output_path)
        result_data = _prepare_data(
            data=self.input_data_without_job_name,
            job_id_column=job_id_column,
            custom_job_name=job_name)
        self.assertIn(constants.DEFAULT_JOB_ID_COLUMN, result_data.columns)
        self.assertIn(
            self.custom_job_name, 
            result_data[constants.DEFAULT_JOB_ID_COLUMN].values)
    
    def test_job_name_param_ignored_if_job_col_exists(self):
        """
        A custom a job name parameter is ignored, if the data contains a
        job id column that is known to it (e.g., from job_spec.yaml).
        """
        job_id_column, job_name = _init_args(
            job_id_column=self.job_id_column,
            custom_job_name="TESTJOB",
            output_path=self.output_path)
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=job_id_column,
            custom_job_name=job_name)
        self.assertIn(self.job_id_column, result_data.columns)
        self.assertNotIn("TESTJOB", result_data[self.job_id_column].values)
        
    # Null values tests

    def test_identifies_null_values(self):
        """
        Missing values are identified correctly.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None)
        _compute_missing_data(
            data=result_data, 
            job_id_column=self.job_id_column, 
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.missing_values_file)))
        result_df = pd.read_csv(os.path.join(
            self.output_path, self.missing_values_file))
        self.assertEqual(result_df.Percentage[0], 50.0)
    
    # Summary statistics tests

    def test_summary_statistics_output_exists(self):
        """
        Summary statistics CSV file is created as expected.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _summarize_data(
            data=result_data, 
            job_id_column=self.job_id_column, 
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.summary_file)))
    
    def test_correlation_analysis_output_exists(self):
        """
        Files for correlation matrix plot and numeric representation is created
        as expected.    
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _correlate_data(
            data=result_data,
            job_id_column=self.job_id_column,
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.correlation_file_csv_job_1)))
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.correlation_file_csv_job_2)))
    
    def test_categorical_summary_output_exists(self):
        """
        Files for target variable aggregations by categorical variables exist.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _summarize_categorical_data(
            data=result_data,
            target_variables=["Metric-1", "Metric-2"],
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.categorical_table_metric1_file)))
    
    # Visualization tests

    def test_histogram_output_exists(self):
        """
        The image files containing histograms have been created.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _plot_histograms(
            data=result_data,
            job_id_column=self.job_id_column,
            output_path=self.output_path) 
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.histogram_file_job_1)))
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.histogram_file_job_2)))
        
    def test_box_whiskers_output_exists(self):
        """
        The images files containing box-whisker plots have been created.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _plot_box_whiskers(
            data=result_data,
            job_id_column=self.job_id_column,
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.box_file_job_1)))
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.box_file_job_2)))
    
    def test_correlation_matrix_exists(self):
        """
        The image files containing correlation matrices have been created.
        """
        result_data = _prepare_data(
            data=self.input_data_with_job_id,
            job_id_column=self.job_id_column,
            custom_job_name=None) 
        _plot_correlations(
            data=result_data,
            job_id_column=self.job_id_column,
            output_path=self.output_path)
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.correlation_file_job_1)))
        self.assertTrue(os.path.exists(os.path.join(
            self.output_path, self.correlation_file_job_2)))
       

if __name__ == "__main__":
    unittest.main()
