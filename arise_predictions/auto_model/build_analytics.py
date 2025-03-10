import logging
import os.path
import pickle
from itertools import product

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import curve_fit
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

from arise_predictions.utils import constants, utils

logger = logging.getLogger(__name__)


# Updated Exponential Function (Only 3 Parameters)
def thpt_generalized_exponential(bb, a, b, c):
    return c - a * np.exp(-b * bb)


class AnalyticalModel:

    def __init__(self, config_file: str = None):

        if config_file:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

        self.input_feature = constants.ANALYTICS_DEFAULT_INPUT_FEATURE if config_file is None else \
            config.get(constants.ANALYTICS_INPUT_FEATURE_NAME, constants.ANALYTICS_DEFAULT_INPUT_FEATURE)
        self.output_feature = constants.ANALYTICS_DEFAULT_OUTPUT_FEATURE if config_file is None else \
            config.get(constants.ANALYTICS_OUTPUT_FEATURE_NAME, constants.ANALYTICS_DEFAULT_OUTPUT_FEATURE)
        self.batch_feature = constants.ANALYTICS_DEFAULT_BATCH_FEATURE if config_file is None else \
            config.get(constants.ANALYTICS_BATCH_FEATURE_NAME, constants.ANALYTICS_DEFAULT_BATCH_FEATURE)
        self.latency_feature = constants.ANALYTICS_DEFAULT_LATENCY_FEATURE if config_file is None else \
            config.get(constants.ANALYTICS_LATENCY_FEATURE_NAME, constants.ANALYTICS_DEFAULT_LATENCY_FEATURE)
        self.throughput_feature = constants.ANALYTICS_DEFAULT_THROUGHPUT_FEATURE if config_file is None else \
            config.get(constants.ANALYTICS_THROUGHPUT_FEATURE_NAME, constants.ANALYTICS_DEFAULT_THROUGHPUT_FEATURE)

    # Building Exponential Database
    def build_exponential_database(self, training_df):
        param_db = {}
        training_params = []

        for (ii, oo), group in training_df.groupby([self.input_feature, self.output_feature]):
            try:
                bb_values = group[self.batch_feature].values
                thpt_values = group[self.throughput_feature].values

                if len(bb_values) > 1:
                    thpt_p10, thpt_p90 = np.percentile(thpt_values, [10, 90])
                    b_p10, b_p90 = np.percentile(bb_values, [10, 90])
                    b_p90 = max(b_p90, b_p10 + 1e-3)  # Ensure a minimum difference

                    # Initial guess
                    initial_guess = [
                        max(thpt_p90 - thpt_p10, 1e-5),  # a: Ensure nonzero
                        1 / max(b_p90 - b_p10, 1e-5),  # b: Avoid zero division
                        max(thpt_p90, 1e-5)  # c: Ensure nonzero
                    ]
                else:
                    initial_guess = [1.0, 0.001, 0.0]

                popt, _ = curve_fit(
                    thpt_generalized_exponential,
                    bb_values,
                    thpt_values,
                    p0=initial_guess,
                    bounds=([0, 1e-5, 0], [1e6, 1, 1e6]),
                    maxfev=10000
                )

                param_db[(ii, oo)] = popt
                training_params.append([ii, oo, *popt])
            except Exception:
                continue

        training_params_df = pd.DataFrame(training_params, columns=[self.input_feature, self.output_feature, "a", "b", "c"])
        return param_db, training_params_df if not training_params_df.empty else None

    def train_xgboost(self, training_params_df):
        if training_params_df is None or training_params_df.empty:
            return None

        # Feature Engineering
        training_params_df["log_ii"] = np.log1p(training_params_df[self.input_feature])
        training_params_df["log_oo"] = np.log1p(training_params_df[self.output_feature])
        training_params_df["log_bb"] = np.log1p(training_params_df[self.input_feature] /
                                                training_params_df[self.output_feature])
        training_params_df["ii_oo_ratio"] = training_params_df[self.input_feature] / \
                                            (training_params_df[self.output_feature] + 1)
        training_params_df["ii_ratio"] = training_params_df[self.input_feature] / \
                                         (training_params_df[self.input_feature] + 1)

        # Features and target variables
        X = training_params_df[[self.input_feature, self.output_feature, "log_ii", "log_oo", "log_bb", "ii_oo_ratio",
                                "ii_ratio"]]
        y = training_params_df[["a", "b", "c"]]

        # Define XGBoost model
        base_model = XGBRegressor(
            n_estimators=5000,
            max_depth=8,
            learning_rate=0.007,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.5,  # L2 regularization
        )

        # Multi-output regression
        model = MultiOutputRegressor(base_model)
        model.fit(X, y)  # Train on full dataset

        return model

    # Function to build and save models for all parameter combinations
    def train_and_save_models(self, file_path: str,  output_path: str):

        expected_features = [self.batch_feature, self.input_feature, self.output_feature, self.latency_feature,
                             self.throughput_feature]

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            logger.error(f"File {file_path} not found. Please provide the correct file path.")
            return

        df_cols = df.columns.values.tolist()
        not_found = [col for col in expected_features if col not in df_cols]

        if not_found:
            not_found_str = ",".join(not_found)
            logger.error(f"The following features are expected but not found in the data: {not_found_str}")
            return

        # Get unique combinations of filtering parameters

        unique_combinations = df[[col for col in df_cols if col not in expected_features]].drop_duplicates()

        for _, row in unique_combinations.iterrows():
            filter_values = row.to_dict()

            # Filter dataset for this combination
            mask = np.logical_and.reduce([(df[k] == v) for k, v in filter_values.items() if pd.notna(v)])
            filtered_df = df[mask]

            if filtered_df.empty:
                logger.warning(f"Skipping {filter_values}, no data found.")
                continue

            total_training_data = []
            for ii_val, bb_val, oo_val in product(df[self.input_feature].unique(), df[self.batch_feature].unique(),
                                                  df[self.output_feature].unique()):
                subset = filtered_df[
                    (filtered_df[self.input_feature] == ii_val) & (filtered_df[self.batch_feature] == bb_val) &
                    (filtered_df[self.output_feature] == oo_val)]
                if not subset.empty:
                    total_training_data.append(subset.iloc[0])

            training_df = pd.DataFrame(total_training_data)
            if training_df.empty:
                logger.warning(f"Skipping {filter_values}, training data is empty.")
                continue

            training_df = training_df[[self.batch_feature, self.input_feature, self.output_feature, self.throughput_feature,
                                       self.latency_feature]]
            param_db, training_params_df = self.build_exponential_database(training_df)
            model = self.train_xgboost(training_params_df)

            # Save model and database
            model_filename = f"{constants.ANALYTICS_MODEL_FILE_PREFIX}_{'_'.join([f'{k}_{v}' for k, v in filter_values.items() if pd.notna(v)])}.pkl"
            param_db_filename = model_filename.replace(constants.ANALYTICS_MODEL_FILE_PREFIX,
                                                       constants.ANALYTICS_PARAMS_FILE_PREFIX).replace(".pkl", ".csv")

            utils.mkdirs(output_path)

            with open(os.path.join(output_path, model_filename), 'wb') as model_file:
                pickle.dump(model, model_file)
            training_params_df.to_csv(os.path.join(output_path, param_db_filename), index=False)

            logger.info(f"Model {model_filename} and params {param_db_filename} written to {output_path}")


