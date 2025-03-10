import time
from datetime import datetime
import pandas as pd

from arise_predictions.utils import constants
import os
import joblib
import errno
from typing import Any
import logging
import shutil, zipfile

logger = logging.getLogger(__name__)


def find_item(obj, key):
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_item(v, key)
            if item:
                return item
    return None


def is_time_format(input_time, time_format):
    try:
        time.strptime(input_time, time_format)
        return True
    except ValueError:
        return False


def from_iso_format(input_time):
    try:
        return datetime.fromisoformat(input_time)
    except ValueError:
        return None


def to_datetime(input_time):
    time_format = get_time_format(input_time)

    if time_format:
        return pd.to_datetime(input_time, format=time_format)
    else:
        return from_iso_format(input_time)


def get_time_format(input_time):
    formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %I:%M:%S %p EST', '%Y-%m-%d %H:%M:%S+00:00']

    for current_format in formats:
        if is_time_format(input_time, current_format):
            return current_format

    return None


def get_duration(start_time, end_time):
    start_time_formatted = to_datetime(start_time)
    if start_time_formatted:
        end_time_formatted = to_datetime(end_time)
        return pd.Timedelta(end_time_formatted - start_time_formatted).seconds
    else:
        raise Exception("Unsupported time format {}".format(start_time))


def adjust_columns_with_duration(columns, start_time_field_name, end_time_field_name):
    # Replace start and end time columns with duration column

    if not start_time_field_name in columns or not end_time_field_name in columns:
        return columns

    adjusted_columns = columns
    if start_time_field_name in columns:
        adjusted_columns.remove(start_time_field_name)
    if end_time_field_name in columns:
        adjusted_columns.remove(end_time_field_name)
    adjusted_columns.append(constants.JOB_DURATION_FIELD_NAME)
    return adjusted_columns


def get_categorical_features(data):
    # numeric_data = data.select_dtypes(include=np.number) # this doesn't work because some numeric
    # columns are assigned with object types, so we'll have to convert to numeric

    # categorical_features = []

    categorical_features = [cols for cols in data.columns if data[cols].dtype == 'object']

    # for column in data.columns.values.tolist():
    #     if pd.isna(pd.to_numeric(data[column], errors='coerce')).all():
    #         categorical_features.append(column)

    return categorical_features

# TODO add exception handling to all IO functions (OSError, FileNotFoundError)


def write_df_to_csv(df: pd.DataFrame, output_path: str, 
                    output_file: str, index: bool = True) -> str:
    mkdirs(output_path)
    path = os.path.join(output_path, output_file)
    df.to_csv(path, index=index)
    return path


def mkdirs(path: str) -> None:
    """
    Create the specified path, if it does not exist yet.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def persist_estimator(estimator: Any, output_path: str, 
                      output_file: str) -> str:
    """
    Write the estimator (e.g., scikit-learn pipeline) to a pickle file.
    """
    # TODO investigate how to make serialization future-proof
    mkdirs(output_path)
    path = os.path.join(output_path, output_file)
    joblib.dump(estimator, path)
    return path


def get_estimator_file_name(estimator_type: str, estimator_name: str, target_variable: str) -> str:
    return f"estimator-{estimator_type}-{estimator_name}"f"-{target_variable}.pkl"


def load_estimator(input_path: str, pickle_file: str) -> Any:
    """
    Load estimator (e.g., scikit-learn pipeline) from a pickle file.
    """
    path = os.path.join(input_path, pickle_file)

    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
    
    return joblib.load(path)


def add_feature_engineering(metadata_path: str, raw_data: pd.DataFrame, feature_engineering: dict[str, str],
                            metadata_parser_class_name: str) -> pd.DataFrame:
    data = raw_data
    if metadata_parser_class_name:
        logger.info("Parsing jobs metadata with class {}".format(metadata_parser_class_name))
        estimation_module = __import__('preprocessing.custom_job_parser', fromlist=[metadata_parser_class_name])
        class_inst = getattr(estimation_module, metadata_parser_class_name)()
    else:
        class_inst = None
    for fe_name, fe_file in feature_engineering.items():
        if fe_name not in raw_data:
            logger.warning(f'Could not engineer feature {fe_name}. Not such feature.')
            continue
        fe_path = os.path.join(metadata_path, constants.JOB_METADATA_DIR, fe_file)
        if class_inst:
            fe_data = getattr(class_inst, "get_metadata_df")(fe_path)
        else:
            fe_data = pd.read_csv(fe_path, sep=',')
        if fe_data is None or fe_data.empty:
            logger.warning(f'Could not engineer feature {fe_name}. Failed loading {fe_file}.')
            continue
        if fe_name not in fe_data:
            logger.warning(f'Could not engineer feature {fe_name}. Not in {fe_file}.')
            continue
        # add suffix to engineered column names
        suffix = '_' + fe_name
        new_cols = [col if col == fe_name else col + suffix for col in fe_data]
        fe_data.columns = new_cols

        logger.info(f'Merging feature engineering for {fe_name} using:\n{fe_data}')
        new_data = data.merge(fe_data, how='left', on=fe_name, suffixes=(None, suffix))  # extra suffix on overlaps
        new_cols = [col for col in new_data if col not in data]
        numeric_cols = set(new_data.select_dtypes(include='number').columns)
        default_values = {col: 0 if col in numeric_cols else "Other" for col in new_cols}
        # @TODO fill value of numeric col -- mean? -1?
        data = new_data.fillna(default_values)

        logger.info(f'** Done feature engineering for {fe_name} using:\n{fe_data}')
    return data


def get_unpacked_path(input_path):
    if zipfile.is_zipfile(input_path):
        input_folder = os.path.join(os.path.dirname(input_path), os.path.splitext(os.path.basename(
            input_path))[0])
        shutil.unpack_archive(input_path, input_folder)
        return input_folder
    else:
        return input_path


def get_best_estimators(rankings: pd.DataFrame, target_var: str, linear_filter: bool = True):

    if not linear_filter:
        best_row = rankings[rankings[constants.AM_COL_TARGET] == target_var].loc[
            lambda filtered: filtered[constants.AM_COL_RANK_MAPE] == filtered[constants.AM_COL_RANK_MAPE].min()]
        return best_row[constants.AM_COL_ESTIMATOR].values[0], best_row[constants.AM_COL_LINEAR].values[0]

    best_linear_estimator_for_target_var = rankings[
        (rankings[constants.AM_COL_TARGET] == target_var) &
        (rankings[constants.AM_COL_LINEAR] == True)].loc[
        lambda filtered: filtered[constants.AM_COL_RANK_MAPE] == filtered[constants.AM_COL_RANK_MAPE].min()][
        constants.AM_COL_ESTIMATOR].values[0]

    best_nonlinear_estimator_for_target_var = rankings[
        (rankings[constants.AM_COL_TARGET] == target_var) &
        (rankings[constants.AM_COL_LINEAR] == False)].loc[
        lambda filtered: filtered[constants.AM_COL_RANK_MAPE] == filtered[constants.AM_COL_RANK_MAPE].min()][
        constants.AM_COL_ESTIMATOR].values[0]

    return best_linear_estimator_for_target_var, best_nonlinear_estimator_for_target_var