
import sys
import pandas as pd
import logging
import os
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from arise_predictions.utils import constants, utils

logger = logging.getLogger(__name__)

"""
Analyzes task/job measurements and prepares various descriptive statistics in
numeric and diagramatic form.
"""


def _init_args(job_id_column=None, custom_job_name=None,
               output_path=None) -> tuple[str, str]:
    """
    :param job_id_column: Name of the column containing the job name.
    Is referred to as 'job id' in job_spec.yaml. 
    :type job_id_column: str
    :param job_name: Name to use for value in job id column. Allows
    user to specify job name if none originally contained in data or our code
    to add a default one so that code can assume a job_id_column.
    :type job_name: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    :returns: Name of job id column and custom job name
    :rtype: tupele[str, str]
    """
    if job_id_column is None:
        job_id_column = constants.DEFAULT_JOB_ID_COLUMN
    job_id_column: str = job_id_column

    if custom_job_name is None:
        custom_job_name = constants.DEFAULT_JOB_NAME
    custom_job_name: str = custom_job_name

    if output_path is None:
        msg = "Must set output_path for data analysis results"
        logger.error(msg)
        raise ValueError(msg)

    # fontsize of the axes title
    plt.rc('axes', titlesize=constants.FONT_SMALL_SIZE)     
    plt.rc('figure', titlesize=constants.FONT_MEDIUM_SIZE)

    return job_id_column, custom_job_name


def _prepare_data(data: pd.DataFrame, job_id_column: str, 
                  custom_job_name: str) -> pd.DataFrame:
    """
    Prepare the preprocessed measurements data for subsequent analysis
    procedures.
    :param data: The preprocessed measurements.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param custom_job_name: Optional name of job name to insert in case none
    exists in data execution history data frame. Enables job analysis code to 
    work the same regardless of whether or not job ids are in data.
    :type custom_job_name: str
    :returns: Data execution history ready for data analysis
    :rtype: pandas.DataFrame
    """
    logger.info("Preparing data for analysis")

    # drop rows without data
    data = data.dropna(how='all')

    # drop columns where all rows are without data
    data = data.dropna(axis=1, how='all')

    # add task_name column if does not exist
    if job_id_column not in data.columns:
        data.insert(0, job_id_column, custom_job_name)

    # convert numeric rows to numeric
    cols = [i for i in data.columns if data[i].dtype.kind in "iufc"]
    for col in cols:
        data[col] = pd.to_numeric(data[col])
    return data
    

def _compute_missing_data(data: pd.DataFrame, job_id_column: str,
                          output_path: str) -> None:
    """"
    Computes statistics about missing values per column/attribute and 
    serializes to a CSV file. 

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Computing missing values")

    job_names = data[job_id_column].unique()

    for job_name in job_names:
        per_job_df = data[data[job_id_column].str.contains(job_name)] 
        per_job_df = per_job_df.drop(job_id_column, axis=1)
        missing_data = per_job_df.isnull().sum()
        missing_percentage = (missing_data / len(per_job_df)) * 100
        missing_df = pd.DataFrame({"Missing Values": missing_data,
                                  "Percentage": missing_percentage})
        missing_df = missing_df.sort_values(
                by="Percentage", ascending=False)
        
        if len(missing_df[missing_df["Missing Values"] > 0]) > 0:
            output_file_missing = f"missing-values-{job_name}.csv"
            written_file = utils.write_df_to_csv(
                missing_df, output_path, output_file_missing)
            logger.info((f"Missing value stats for {job_name}" 
                        f"saved to {written_file}"))
        else:
            logger.info(f"No missing values found for {job_name}.")
   

def _summarize_data(data: pd.DataFrame, job_id_column: str, 
                    output_path: str) -> None:
    """
    Computes summary statistics and writes results to a CSV file.

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Summarizing data")

    output_file_summary = "descriptive-stats.csv"
    summary_df = data.groupby(job_id_column).describe()
    written_file = utils.write_df_to_csv(
        summary_df, output_path, output_file_summary)
    logger.info(f"Summary statistics written to {written_file}.")
    

def _correlate_data(data: pd.DataFrame, job_id_column: str,
                    output_path: str) -> None:
    """
    Computes pairwise correlations and writes to a CSV file.

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Computing correlations")

    job_names = data[job_id_column].unique()

    for job_name in job_names:
        corr_df = data[data[job_id_column].str.contains(job_name)]
        corr_df = corr_df.drop(job_id_column, axis=1)
        corr_df = corr_df.select_dtypes(include=constants.NUMERICS)
        corr_df = corr_df.corr(method="pearson")
        output_file_corr = f"correlations-{job_name}.csv"
        written_file = utils.write_df_to_csv(
            corr_df, output_path, output_file_corr)
        logger.info(f"Correlations for {job_name} saved to {written_file}")


def _summarize_categorical_data(data: pd.DataFrame, 
                                target_variables: list[str],
                                output_path: str) -> None:
    """
    Computes aggregations of each target variable per value of a
    categorical variable.
    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data. 
    :type raw_data: pandas.DataFrame
    :param target_variables: List of column names containing target 
    variables (from job_spec.yaml)
    :type target_variables: list[str]
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info(("Computing target variable aggregations for categorical" 
                " variables"))

    categorical_variables: list[str] = utils.get_categorical_features(data)
    logger.info(f"Found categorical variables: {categorical_variables}")

    # We remove start_time and end_time fields and instead rely on 
    # a duration field being present. 
    # TODO discuss a better long-term approach
    target_variables = [x for x in target_variables 
                        if not x.endswith("start_time") 
                        or not x.endswith("end_time")]
    target_variables.insert(0, constants.JOB_DURATION_FIELD_NAME)
    
    # We remove target variables whose columns have no data
    target_variables = [x for x in target_variables if x in data.columns]
    logger.info(f"Analyzing for target variables: {target_variables}")

    for target_var in target_variables:
        agg_df = data.groupby(categorical_variables).agg(
            target_var_min=(target_var, "min"),
            target_var_mean=(target_var, "mean"),
            target_var_max=(target_var, "max"))
        output_file_categorical = f"categorical-stats-{target_var}.csv"
        written_file = utils.write_df_to_csv(
            agg_df, output_path, output_file_categorical)
        logger.info(f"Categorical summary written to {written_file}")


def _plot_histograms(data: pd.DataFrame,
                     job_id_column: str,
                     output_path: str) -> None:
    """
    Plots histograms of all numeric variables and stores them to a single 
    PDF file.

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Generating histograms")
    
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    nrows = 3
    ncols = 1

    for job_name, data_slice in data.groupby(job_id_column):
        output_file = os.path.join(
            output_path, f"histogram-{job_name}.pdf")
        pdf = PdfPages(output_file)
        data_slice = data_slice.drop(job_id_column, axis=1)
        data_slice = data_slice.select_dtypes(include=constants.NUMERICS)
        cols = data_slice.columns

        for i, col in enumerate(cols):
            j = i % (nrows * ncols)

            if j == 0:
                fig = plt.figure(figsize=(8, 6))
            
            ax = fig.add_subplot(nrows, ncols, j + 1)
            ax.set_title(f"{job_name} - {col}")
            data_slice[col].plot(kind="hist", grid=True, ax=ax, bins=15)
    
            if j == (nrows * ncols) - 1 or i == len(cols) - 1:
                fig.tight_layout()
                pdf.savefig(fig)
                logger.info(
                    f"Histograms for {job_name} saved to {output_file}")
        pdf.close()
    

def _plot_box_whiskers(data: pd.DataFrame, job_id_column: str,
                       output_path: str) -> None:
    """
    Plots box-whisper plots and stores them to a single PDF file. 

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Generating box-whisker plots")

    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    nrows = 1
    ncols = 4

    for job_name, data_slice in data.groupby(job_id_column):
        output_file = os.path.join(output_path, f"box-{job_name}.pdf")
        pdf = PdfPages(output_file)
        data_slice = data_slice.drop(job_id_column, axis=1)
        data_slice = data_slice.select_dtypes(include=constants.NUMERICS)
        cols = data_slice.columns

        for i, col in enumerate(cols):
            j = i % (nrows * ncols)

            if j == 0:
                fig = plt.figure(figsize=(12, 5))
            
            ax = fig.add_subplot(nrows, ncols, j + 1)
            ax.set_title(f"{job_name} - {col}")
            data_slice[col].plot(kind="box", grid=True, ax=ax)
    
            if j == (nrows * ncols) - 1 or i == len(cols) - 1:
                fig.tight_layout()
                pdf.savefig(fig)
                logger.info(
                    f"Box plot for {job_name} saved to {output_file}")
        pdf.close()
        

def _plot_correlations(data: pd.DataFrame, job_id_column: str,
                       output_path: str) -> None:
    """
    Plots correlation matrices for each job.

    :param data: Data execution history data preprocessed from
    measurements and prepared by _prepare_data.
    :type data: pandas.DataFrame
    :param job_id_column: Name of column containing job ids
    :type job_id_column: str
    :param output_path: Path to directory to use for data analysis files.
    :type output_path: str
    """
    logger.info("Generating correlation matrix plots")

    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    fig, ax = plt.subplots()

    for job_name, data_slice in data.groupby(job_id_column):
        data_slice = data_slice.drop(job_id_column, axis=1)
        data_slice = data_slice.select_dtypes(include=constants.NUMERICS)
        fig = plt.figure(figsize=(14, 14))
        ax = fig.add_subplot(111)
        cax = ax.matshow(data_slice.corr(), vmin=-1, vmax=1)
        ticks = np.arange(0, len(data_slice.columns), 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(data_slice.columns, rotation=45)
        ax.set_yticklabels(data_slice.columns, rotation=45)
        fig.colorbar(cax)
        plt.title(f"{job_name}")
        output_file = os.path.join(
            output_path, f"correlation-{job_name}.png")
        plt.savefig(output_file, dpi=300)


# TODO complete implementation and test
def analyze_job_data(raw_data: pd.DataFrame, job_id_column: str = None,
                     custom_job_name: str = None, output_path: str = None,
                     target_variables: list[str] = None):
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("Beginning descriptive job analysis.")

    job_id_column, custom_job_name = _init_args(
        job_id_column=job_id_column, custom_job_name=custom_job_name, 
        output_path=output_path)
    prepared_data = _prepare_data(data=raw_data, job_id_column=job_id_column,
                                  custom_job_name=custom_job_name)
    _compute_missing_data(data=prepared_data, job_id_column=job_id_column,
                          output_path=output_path) 
    _summarize_data(data=prepared_data, job_id_column=job_id_column, 
                    output_path=output_path)
    _correlate_data(data=prepared_data, job_id_column=job_id_column, 
                    output_path=output_path)
    _summarize_categorical_data(data=prepared_data, 
                                target_variables=target_variables, 
                                output_path=output_path)
    _plot_histograms(data=prepared_data, job_id_column=job_id_column, 
                     output_path=output_path)
    _plot_box_whiskers(data=prepared_data, job_id_column=job_id_column, 
                       output_path=output_path)
    _plot_correlations(data=prepared_data, job_id_column=job_id_column,
                       output_path=output_path)
    logger.info(f"Wrote descriptive job analysis to {output_path}.")
