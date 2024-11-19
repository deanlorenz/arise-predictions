# Using the ARISE Prediction UI
The ARISE prediction tool provides an intuitive web interface for estimating resource requirements 
and performance metrics for AI workloads. 
This document details the features of the ARISE UI, how to configure input/output parameters, 
interpret results, and use filters effectively. 
Additionally, a usage example is provided to demonstrate its functionality.

## Overview of the ARISE Prediction UI
The ARISE prediction landing page is designed to guide users in predicting resource 
usage and execution time for AI workloads based on historical data or performance benchmarks. 
The UI supports input configurations, 
customizable output parameters, 
and result filtering for better analysis.

## Key Sections
- **Prediction Configuration Panel:** Located on the left sidebar, this allows users to define input 
parameters for predictions, output parameters of prediction and other required configurations for the
performing the prediction process, including a prediction button.
- **Input Configuration Panel:** Part of the sidebar, enabling the selection of input configuration fields.
Each of the fields can be numeric or categorical. By setting ranges and values the user can define 
the prediction space. 
- **Output Configuration Panel:** Part of the sidebar, enabling the selection of output configuration fields.
- **Main Display Area:** Presents prediction results and enables additional interactions.
- **Interactive Query Panel:** At the bottom right, AI Bot that allows users to ask questions or explore 
additional capabilities.


## Configuring Input Parameters
The input parameters are set in the Prediction Configuration Panel. 
Each parameter is essential for accurate prediction results.
The list of fields is dynamic and based on the provided data-set and training.
Follows is a detailed explanation of all configurable input parameters
when using the `MLCommons` dataset:

1. **# of Accelerators:**   
Purpose: Define the number and type of GPUs or accelerators to be used.
Configuration: Use the slider to select the number of accelerators (range: 0-8).
1. **# of Nodes:**     
Purpose: Specify the number of compute nodes.
Configuration: Adjust the slider (range: 1-4).
1. **# Accelerator:**  
Mult select dropdown options include supported models, such as NVIDIA H100.
1. **Host Processor Core Count:**  
Purpose: Define the number of CPU cores available on the host system.
Configuration: Adjust the slider (range: 0-128).
1. **Model MLC:** 
Purpose: Specify the AI model being evaluated.
Configuration: Use the dropdown to select from available models, e.g., llama2-70b.
1. ** Processor:**  
Purpose: Select the processor type for computations.
Configuration: Choose from multiple processor options (e.g., Intel Xeon, AMD EPYC).
1. ** Scenario:**  
Purpose: Define the workload scenario.
Configuration: Options include Offline and Server.

## Configuring Output Parameters
In addition, the Output Configuration Panel allows users to select the desired prediction metric. 
For example for the `MLCommons` dataset:

1. **Tokens Per Second:**  
Purpose: Displays the model's token generation rate based on the configuration.
Configuration: Check the box next to the desired output metric.

> Note: Multiple outputs can be selected for a comprehensive view.

## Interpreting the Results Table
Once inputs and outputs are configured, clicking the Predict button displays results in the main area. 
For the `MLCommons` data-set, The table provides:

**Resource Estimation:** Expected hardware and node usage.
**Performance Metrics:** Tokens per second or other selected metrics.
**Scenario Details:**  Summary of the input configuration used.

Example Columns:  

| Metric            | Value         |
|:------------------|:--------------|
| Tokens Per Second | 4500          |
| Accelerators Used | 	3            |
| Accelerator       | (NVIDIA H100) |
| CPU Cores	        | 42            |


## Using Filters for Analysis
The result table includes a filtering feature for narrowing down results:

- **Sort by Metric:**   
Organize data based on performance or resource usage allows accenting or descending sorting
 according to required focus area.
- **Dropdown Filters:**  
Refine results based on categories such as accelerators or nodes 
and numeric selection such as `Tokens Per Second`   
How to use: Pressing the `Add filters` button opens a combo box that allows 
selection of filtering columns.
For each of the selected columns to filter, either categorical or numeric selection box
allows narrowing down the table to focus only on the desired scope of data.


## Example Use Case
**Scenario:** You want to estimate the resources required to achieve 5000 tokens per second for an AI model using NVIDIA H100 GPUs.

Steps:

1. Open the ARISE prediction page.
2. Configure the following inputs:
- Accelerators: 3 
- Nodes: 1
- Accelerator: NVIDIA H100
- Host Processor Core Count: 42
- Model MLC: llama2-70b
- Processor: Intel Xeon
- Scenario: Server
3. Configure the following outputs:
- Tokens Per Second: Check this output field 
4. Click Predict

**Review the results**:

1. The table shows the predicted tokens per second (e.g., 4500) and other metrics like resource usage, etc.
2. Click `Add filters`  
3. select `Tokens Per Second`
4. Use the slider to focus the `Tokens Per Second` column around 5000 tokens per second

> *Notes and Recommendations:*  
> 
> **Model Training:** Ensure the prediction model is pre-trained on workload data for accurate results.  
> 
> **Patience:** Predictions may take time based on the complexity of configurations.  
> 
> **Iterative Adjustments:** Modify inputs to explore how different configurations impact performance. 

