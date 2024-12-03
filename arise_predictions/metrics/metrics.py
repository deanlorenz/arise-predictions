import numpy as np
from typing import Tuple

from sklearn.metrics import (
    make_scorer,
    mean_squared_error, 
    mean_absolute_percentage_error, 
    r2_score
    )
                             
"""
Custom ML performance metrics and related utilities.
"""


def normalized_root_mean_squared_error_minmax(y_true, y_pred):
    rmse_mean = np.sqrt(mean_squared_error(y_true, y_pred))
    target_variable_min, target_variable_max = get_min_max_from_array(y_true)
    nrmse = rmse_mean / (target_variable_max - target_variable_min)
    return nrmse


def compute_test_metrics(y_true, y_pred):
    mape_mean_test_all = [mean_absolute_percentage_error([y_t], [y_p]) for y_t, y_p in zip(y_true, y_pred)]
    mape_mean_test = np.average(mape_mean_test_all)
    mape_std_test = np.std(mape_mean_test_all)
    nrmse_mean_test = normalized_root_mean_squared_error_minmax(y_true, y_pred)
    r2_mean_test = r2_score(y_true, y_pred)
    return mape_mean_test, mape_std_test, nrmse_mean_test, r2_mean_test


def create_scorers():
    scoring = {
        "neg_mean_absolute_percentage_error": 
            "neg_mean_absolute_percentage_error", 
        "neg_normalized_root_mean_squared_error(minmax)": make_scorer(
            normalized_root_mean_squared_error_minmax, 
            greater_is_better=False), 
        "neg_root_mean_squared_error": "neg_root_mean_squared_error", 
        "neg_mean_squared_error": "neg_mean_squared_error", 
        "neg_mean_absolute_error": "neg_mean_absolute_error", 
        "r2": "r2"
    }
    return scoring


def get_min_max_from_array(array) -> Tuple[float, float]:
    min = np.amin(array)
    max = np.amax(array)
    return min, max
