# Set the default target
.DEFAULT_GOAL := help
VENV_NAME := .venv

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

venv_create:
	python -m venv $(VENV_NAME)

venv_install_requirements:
	@source $(VENV_NAME)/bin/activate && \
	@pip install -r requirements.txt && \
	deactivate

install_requirements:
	@pip install -q -r requirements.txt

##@ Development
run: install_requirements ## Run the code
	python src/main.py
	
venv_run: venv_create venv_install_requirements ## Run the code in python venv
	@source $(VENV_NAME)/bin/activate && \
	python src/main.py && \
	deactivate

##@ Development-synthetic

analyze-jobs-mlcommons: install_requirements ## Perform statistical analysis on MLCommons data
	python src/main.py analyze-jobs --input-path examples/MLCommons --job-spec-file-name job_spec.yaml

auto-build-models-mlcommons: install_requirements ## Search for best predicting model among different linear and decision tree regressors
	python src/main.py auto-build-models --input-path examples/MLCommons --config-file config/small-auto-model-search-config.yaml

predict-mlcommons: install_requirements auto-build-models-mlcommons ## Predict values for the input space defined in the configuration based on the computed model
	python src/main.py predict --input-path examples/MLCommons --model-path examples/MLCommons/ARISE-auto-models --config-file config/example-demo-mlcommons-config.yaml

demo-predict-mlcommons: install_requirements auto-build-models-mlcommons ## Predict values for the input space defined in the configuration based on the computed model, and compare with ground truth
	python src/main.py demo-predict --input-path examples/MLCommons --model-path examples/MLCommons/ARISE-auto-models --config-file config/example-demo-mlcommons-config.yaml


