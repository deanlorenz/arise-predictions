import pandas as pd
import os
from cmd.cmd import parse_args, get_args
from job_statistics.analyze_jobs import analyze_job_data
from auto_model.build_models import auto_build_models
from perform_predict.predict import demo_predict, PredictionInputSpace
from utils import constants
from preprocessing import job_parser
from utils import utils
import logging
import yaml

logger = logging.getLogger(__name__)


def load_spec(spec_file_name):
    # analyzing job spec file
    job_spec_file = os.path.join(get_args().input_path, spec_file_name)
    logger.info('Analyzing job spec file: %s', job_spec_file)
    loaded_job_spec = job_parser.parse_job_spec(job_spec_file)
    if not loaded_job_spec:
        logger.error("Failed to load job spec")
        raise Exception
    return loaded_job_spec


def execute_preprocess(job_spec):

    inputs = sorted(list(job_spec[0]))
    outputs = sorted(list(job_spec[1]))
    identifiers = sorted(list(job_spec[2]))
    start_time_field_name = job_spec[3]
    end_time_field_name = job_spec[4]
    job_parser_class_name = job_spec[5]
    job_entry_filter = job_spec[6]
    feature_engineering = job_spec[7] if len(job_spec) > 7 else None
    metadata_parser_class_name = job_spec[8] if len(job_spec) > 8 else None

    # processing history ( if not done in the past )
    analyzed_history_file = os.path.join(
        get_args().input_path, constants.JOB_HISTORY_FILE_NAME + ".csv")
    return get_history(analyzed_history_file, identifiers+inputs, outputs, start_time_field_name, end_time_field_name,
                       job_parser_class_name, job_entry_filter, feature_engineering, metadata_parser_class_name)


def execute_analyze_jobs():
    loaded_job_spec = load_spec(get_args().job_spec_file_name)
    outputs = sorted(list(loaded_job_spec[1])) 
    identifiers = sorted(list(loaded_job_spec[2]))

    # processing history ( if not done in the past )
    history_data, history_file = execute_preprocess(loaded_job_spec)

    if history_data is None or history_data.empty:
        logging.error(("No historical data could be retrieved from given" 
                       " location {}").format(get_args().input_path))
    else:
        logging.info("Invoking job analysis")
        # Note that this assumes a single job id column is specified
        # (identifiers[0])
        job_id_column = None
        if identifiers:
            job_id_column = identifiers[0]
        analyze_job_data(raw_data=history_data, job_id_column=job_id_column,
                         custom_job_name=get_args().custom_job_name,
                         output_path=os.path.join(get_args().input_path, 
                                                  constants.JOB_ANALYSIS_PATH),
                         target_variables=outputs)


def execute_auto_build_models():
    loaded_job_spec = load_spec(get_args().job_spec_file_name)
    outputs = sorted(list(loaded_job_spec[1])) 

    # processing history ( if not done in the past )
    history_data, history_file = execute_preprocess(loaded_job_spec)

    if history_data is None or history_data.empty:
        logging.error(("No historical data could be retrieved from given" 
                       " location {}").format(get_args().input_path))
    else:
        logging.info("Invoking auto model search and build")
        auto_build_models(raw_data=history_data, 
                          config_file=get_args().config_file,
                          target_variables=outputs, 
                          output_path=os.path.join(
                              get_args().input_path, 
                              constants.AM_OUTPUT_PATH_SUFFIX), 
                          leave_one_out_cv=get_args().leave_one_out_cv,
                          feature_col=get_args().feature_column,
                          low_threshold=get_args().low_threshold,
                          high_threshold=get_args().high_threshold,
                          single_output_file=get_args().single_output_file)


def execute_demo_predict():
    loaded_job_spec = load_spec(get_args().job_spec_file_name)

    # processing history ( if not done in the past )
    history_data, history_file = execute_preprocess(loaded_job_spec)

    if history_data is None or history_data.empty:
        logging.error(("No historical data could be retrieved from given" 
                       " location {}").format(get_args().input_path))
    else:
        logging.info("Invoking demo predict")
        demo_predict(
            original_data=history_data,
            config=get_predict_config(get_args().config_file),
            estimator_path=get_args().model_path,
            feature_engineering=None if get_args().ignore_metadata else loaded_job_spec[7],
            metadata_parser_class_name=loaded_job_spec[8],
            metadata_path=get_args().input_path,
            output_path=os.path.join(
                get_args().input_path, constants.PRED_OUTPUT_PATH_SUFFIX))


def execute_predict():
    loaded_job_spec = load_spec(get_args().job_spec_file_name)

    logging.info("Invoking predict")
    demo_predict(
        original_data=None,
        config=get_predict_config(get_args().config_file),
        estimator_path=get_args().model_path,
        feature_engineering=None if get_args().ignore_metadata else loaded_job_spec[7],
        metadata_parser_class_name=loaded_job_spec[8],
        metadata_path=get_args().input_path,
        output_path=os.path.join(
            get_args().input_path, constants.PRED_OUTPUT_PATH_SUFFIX))


def get_predict_config(config_file: str) -> PredictionInputSpace:
    logger.info(f"Reading YAML configuration: {config_file}")

    with open(config_file, "r") as f:
        config_dict = yaml.safe_load(f)

    return PredictionInputSpace(config_dict[constants.PRED_CONFIG_FIXED],
                                config_dict[constants.PRED_CONFIG_VARIABLE],
                                config_dict.get(constants.PRED_CONFIG_INTERPOLATION, []),
                                config_dict[constants.PRED_CONFIG_ESTIMATORS])


def get_history(history_file, inputs, outputs, start_time_field_name, end_time_field_name, job_parser_class_name,
                job_entry_filter, feature_engineering, metadata_parser_class_name):
    if os.path.exists(history_file) and not get_args().reread_history:
        logging.info("using already processed history")
        history_data = pd.read_csv(history_file)
        history_data = history_data[utils.adjust_columns_with_duration(history_data.columns.values.tolist(),
                                                                       start_time_field_name,
                                                                       end_time_field_name)]
    else:
        logging.info("processing historical jobs")
        history_data, history_file = job_parser.collect_jobs_history(
            get_args().input_path + "/" + constants.JOB_DATA_DIR, get_args().input_path, inputs, outputs,
            start_time_field_name, end_time_field_name, get_args().input_file, job_parser_class_name, job_entry_filter,
            None if get_args().ignore_metadata else feature_engineering, metadata_parser_class_name,
            get_args().input_path)
    return history_data, history_file


def main():
    if not parse_args():
        global logger
        logger.error('Failed to parse command line arguments')
        exit(1)
    level = logging.getLevelName(get_args().loglevel.upper())
    print("level: %d" % level)
    print("cmd_args: %s" % get_args())

    logger = logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # According to the selected command, call the appropriate function
    if get_args().command == 'preprocess':
        execute_preprocess(load_spec(get_args().job_spec_file_name))
    elif get_args().command == 'analyze-jobs':
        execute_analyze_jobs()
    elif get_args().command == 'auto-build-models':
        execute_auto_build_models()
    elif get_args().command == 'demo-predict':
        execute_demo_predict()
    elif get_args().command == 'predict':
        execute_predict()
    else:
        logger.error('Invalid command!')
        logger.info(
            'For development purpose we will execute the get-stats command')
        logger.info('This will be removed in production')
        from cmd.cmd import cmd_args
        cmd_args.command = "get-stats"
        cmd_args.input_path = "examples/MLCommons"
        cmd_args.reread_history = False
        execute_analyze_jobs()


if __name__ == '__main__':
    main()
