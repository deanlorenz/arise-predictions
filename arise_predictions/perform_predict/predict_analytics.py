import pickle
import pandas as pd
import numpy as np
import logging
import sys
import os
import yaml
from typing import Tuple

from arise_predictions.utils import utils, constants
from arise_predictions.perform_predict.predict import PredictionInputSpace, _create_input_space

logger = logging.getLogger(__name__)


# Load precomputed models
def load_precomputed_models(param_db_file, xgb_model_file):
    try:
        with open(param_db_file, 'rb') as f:
            param_db = pickle.load(f)
        with open(xgb_model_file, 'rb') as f:
            model = pickle.load(f)
        return param_db, model
    except FileNotFoundError:
        return None, None


class AnalyticalPredictor:
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

    # Predict throughput for given values
    def predict_thpt(self, complement_df, param_db, model):
        predictions = []

        for _, row in complement_df.iterrows():
            ii, oo, bb = row[self.input_feature], row[self.output_feature], row[self.batch_feature]

            # Retrieve parameters from precomputed param_db
            params = param_db.get((ii, oo))

            if params is None and model is not None:
                # Predict parameters using the precomputed XGBoost model
                x_input = np.array([[ii, oo, np.log1p(ii), np.log1p(oo), np.log1p(ii / oo), ii / (oo + 1), ii / (ii + 1)]])
                params = model.predict(x_input)[0]

            if params is not None:
                a, b, c = params
                predicted_thpt = utils.thpt_generalized_exponential(bb, a, b, c)
            else:
                predicted_thpt = np.nan  # If parameters are missing

            predictions.append(predicted_thpt)

        return np.array(predictions)

    def xgb_analytical_combo(self, row_to_predict: pd.DataFrame, estimator_path: str) -> Tuple[int, int]:
        # Construct filename based on provided values

        filter_values_list = [(feature_name, row_to_predict[feature_name][0]) for feature_name
                              in row_to_predict.columns.values.tolist()
                              if feature_name not in [self.input_feature, self.output_feature, self.batch_feature]]

        filter_values = dict(filter_values_list)

        model_filename = f"{constants.ANALYTICS_MODEL_FILE_PREFIX}_{'_'.join([f'{k}_{v}' for k, v in filter_values.items() if v is not None])}.pkl"
        param_db_filename = model_filename.replace(constants.ANALYTICS_MODEL_FILE_PREFIX,
                                                   constants.ANALYTICS_PARAMS_FILE_PREFIX).replace(".pkl", ".csv")

        ii = row_to_predict[self.input_feature][0]
        oo = row_to_predict[self.output_feature][0]
        bb = row_to_predict[self.batch_feature][0]

        try:
            # Load model and parameter database
            with open(os.path.join(estimator_path, model_filename), 'rb') as model_file:
                model = pickle.load(model_file)
            param_db = pd.read_csv(os.path.join(estimator_path, param_db_filename))
        except FileNotFoundError:
            logger.warning(f"Model file {model_filename} not found. Ensure models are pre-trained.")
            return -1, -1

        # Create test input
        test_df = pd.DataFrame([[bb, ii, oo]], columns=[self.batch_feature, self.input_feature, self.output_feature])

        # Predict throughput using the preloaded model
        predictions = self.predict_thpt(test_df, param_db, model)

        return predictions[0] if predictions.size > 0 else -1, (oo * bb) / predictions[0] \
            if predictions.size > 0 else -1

    def _run_predictions(self, data_to_predict: pd.DataFrame, estimator_path: str) -> Tuple[str, pd.DataFrame]:

        predictions_columns = data_to_predict.columns.values.tolist() + [self.throughput_feature, self.latency_feature]

        predictions = pd.DataFrame(columns=predictions_columns)
        for index, row in data_to_predict.iterrows():
            thpt, latency = self.xgb_analytical_combo(
                row_to_predict=pd.DataFrame([row.values], columns=data_to_predict.columns.values.tolist()),
                estimator_path=estimator_path)
            if thpt > -1:
                new_row = pd.DataFrame([row.values.tolist()+[thpt, latency]], columns=predictions_columns)
                if predictions.empty:
                    predictions = new_row
                else:
                    predictions.reset_index(drop=True, inplace=True)
                    predictions = pd.concat([predictions, new_row])

        return predictions

    def predict(self, predictions_config: PredictionInputSpace, estimator_path: str, output_path: str = None) -> \
            Tuple[str, pd.DataFrame]:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logger.info("Beginning analytic predict")
        _, input_space_df = _create_input_space(
            input_config=predictions_config,
            original_data=None,
            output_path=output_path
        )

        predictions_df = self._run_predictions(data_to_predict=input_space_df, estimator_path=estimator_path)

        output_file_preds = "predictions-analytics.csv"
        path = utils.write_df_to_csv(
            df=predictions_df,
            output_path=output_path,
            output_file=output_file_preds)

        logger.info(f"Analytic predict outputs written to {output_path}")

        return path, predictions_df
