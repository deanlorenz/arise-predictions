# arise-insights: AI Right Sizing Engine

AI Right Sizing Engine (ARISE) is a tool for predicting required resources and execution time of an AI workload, based 
on historical executions or performance benchmarks of similar workloads (a workload dataset). ARISE is intended to 
support configuration decision-making for platform engineers or data scientists operating with AI stacks. 

ARISE parses and preprocesses the given workloads dataset into a standard format, provides descriptive statistics, 
trains predictive models, and performs predictions based on the models. See [Instructions for running the CLI](#running-the-cli-on-sample-data) for 
details on the commands to invoke the above operations. To use these commands, in addition to the workload dataset, you 
need to provide in your input path a `job_spec.yaml` file indicating the metadata inputs and outputs of your data.
See [this example](examples/MLCommons/job_spec.yaml) of a job spec.

## Installing and running the CLI

### Installing from a repo snapshot

- Clone the repo or download codebase zip

- Install the CLI

To install the CLI in a virtual environment (this would be the preferred installation mode to keep the 
installation isolated and avoid version conflicts), run the commands:

```buildoutcfg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows users should run:

```buildoutcfg
python3 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Execute tests

From the project root directory:

```bash
PYTHONPATH=src/ python -m unittest -v
```

To see the log messages for failing tests, use the buffer command (and use
`tests.utils.logger_redirector` in your test case). See `tests.test_analyze.py`
as an example.

```bash
PYTHONPATH=src/ python -m unittest -v --buffer
```

Running the tests on a single test case:

```bash
PYTHONPATH=src/:tests/ python -m unittest -v --buffer tests/test_build_models.py
```

### Running the CLI on sample data

There are four supported commands:

1. `analyze-jobs` provides descriptive statistics on the metadata inputs (workload
measurements) and generates a number of spreadsheets and plots in a
subdirectory called `job-analysis`. The data should be provided in a folder
called `data` in the given `input-path`.

```bash
python src/main.py analyze-jobs --input-path examples/MLCommons
```

It is also possible to specify the job spec file and metadata input explicitly:

```bash
python src/main.py analyze-jobs --input-path examples/MLCommons --reread-history --job-spec-file-name job_spec.yaml --input-file inference_data_tokens.csv --custom-job-name inference-thpt
```

In the above example, we also specify a custom job name. In this example data
set there is no job id column. With `--custom-job-name, we instruct the code to
insert such a column with the given job name as values.  This tends to improve
the output of the descriptive job analysis  (e.g., labels in plots).

2. `auto-build-models` performs a hyperparameter search over the models and
   parameter space specified in a configuration file (cf.,
   `config/default-auto-model-search-config.yaml`) and finds the best model and
   its hyperparameter settings for each target variable in the data. It attempts
   to build one best model per target variable in the metadata outputs based on
   the metadata inputs. 

Example:

```bash
python src/main.py auto-build-models --input-path examples/MLCommons --reread-history
```

The output models, their relative ranking, and the cross validation results are all stored in a folder named 
`ARISE-auto-models` which is created in the given input path.

If you do not specify an option for `--config-file`, it uses the default one in
`config/default-auto-model-search-config.yaml`. There is a config file that
defines a much smaller parameter search space and hence completes in a shorter
time. You can make use of it like this:

```bash
python src/main.py auto-build-models --input-path examples/MLCommons --reread-history --config-file config/small-auto-model-search-config.yaml
```

By default, `auto-build-models` performs 10-fold cross validation. If you want to perform instead `leave-one-group-out (logo)`
cross validation, add the cflag `--leave-one-out-cv`, which takes as an argument a list of one or more feature names to 
group py, separated by commas.

For example, the following command will build models using logo cross validation on values of LLM name.
That is, in each iteration it will use a specific LLM as the test set, and all other data as the training set. 

```bash
python src/main.py auto-build-models --input-path examples/MLCommons --leave-one-out-cv "Model MLC"
```

In addition to the above, we can also let `auto-build-models` search for models that are tuned for
extrapolation. That is, you can let ARISE build a model that performs
*relatively* well when asked to predict on inputs that are outside the range of
values seen for this feature during training. This is an experimental feature
whose performance we expect to improve with time. Currently, only a single
extrapolated feature is supported and the training data needs a number of
different data points or levels for this feature to have an opportunity to learn
to extrapolate.
You specify the name of the input feature on which to extrapolate
(`--feature-column`) as well as a low and or high threshold (`--low-threshold`,
`--high-treshold`) which define the extrapolation region to train on. The
thresholds should be chosen from within the range of values that exist in the
training data, so that ARISE can define regions used for training and for
testing the extrapolation performance of the resulting models. For example: 

```bash
python src/main.py auto-build-models --input-path examples/MLCommons --reread-history --feature-column "# of Accelerators" --high-threshold 8
```

3. `predict` generates estimated values for metadata outputs given metadata input values. It should 
be run after `auto-build-models` command and uses its output. The `--model-path` flag is where the models created by `auto-build-models` are located.
The `job_spec.yaml` file should be under the `--input-path`. Predict requires to specify a model name and input space configuration.
It generates the space of input features according to the configuration and uses models previously built with `auto-build-models` to run predictions on this
input space for the target variables indicated in the same configuration file.

An example configuration file: [example-demo-mlcommons-config.yaml](config/example-demo-mlcommons-config.yaml).

The `--config-file` argument is optional (uses example configuration file if no alternative is specified).

```bash
python src/main.py predict --input-path examples/MLCommons --config-file
config/example-demo-mlcommons-config.yaml --model-path examples/MLCommons/ARISE-auto-models
```

The input space defined by the configuration file and ARISE predictions for each input combination in this space are  
stored in a folder named `ARISE-predictions` which is created in the given input path.

4. `demo-predict` is a version of predict that facilitates demos by ranking
    predictions and comparing predictions with ground truth where available. 

    The `--input-path` should point historic or benchmark input data so `demo-predict` could compare predictions with available
    ground truth (as far as is possible). The script needs to have the path to
    the directory containing the serialized models built by `auto-build-models`.
    Other parameters are taken from the configuration file.

```bash
python src/main.py demo-predict --input-path examples/MLCommons --config-file
config/example-demo-mlcommons-config.yaml --model-path examples/MLCommons/ARISE-auto-models
```

In addition to the outputs described for the `predict` command, `demo-predict` will also create a file named 
`predictions-with-ground-truth.csv`, containing the predicted versus ground truth values and the resulting MAPE error, 
for any input combination in the defined input space that appears also in the given ground truth data. 

To use all the above commands, you need to provide in your input path a `job_spec.yaml` file indicating the 
metadata inputs and outputs of your data. See [this example](examples/MLCommons/job_spec.yaml) of a job
spec.

The default log level is `DEBUG`. You can change by specifying a different log
level as in the following example:

```bash
python src/main.py --loglevel info analyze-jobs
```

## Historical data

The data consists of historical workload executions and/or performance benchmarks. Examples of potential properties of 
workloads that can be considered:

1. Input data size and data complexity-related properties
2. Hyper-parameters
3. Workload task
4. LLM
5. GPU configuration
6. Total execution time 
7. Throughput and latency
8. Consumed resources: number of workers, CPU, GPU, and memory per worker
9. Job status (success, fail/abort, etc.)

The data is divided into 'job-metadata-inputs': the properties of the workload that are known before it starts running 
(e.g., items 1-5 above), and 'job-metadata-outputs': properties of the workload execution and output that are known only 
once the workload completes (e.g., items 6-9 above). Our goal is to use AI to learn from historical executions the 
functions that describe the relations between the metadata inputs and metadata outputs, so that we can predict metadata 
outputs based on metadata inputs.

The above workload properties can be configured and extended per use case, using the `job_spec.yaml` file. 
See [this example](examples/MLCommons/job_spec.yaml) of a job spec, and [Instructions for running the CLI](#running-the-cli-on-sample-data) 
for more details.