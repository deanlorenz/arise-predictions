# Using the ARISE Prediction UI

The ARISE Prediction Tool provides an intuitive web interface for estimating resource requirements and performance metrics for AI workloads. This document explains the features of the ARISE UI, how to configure input and output parameters, interpret results, and use filters effectively. A usage example is also provided to demonstrate its functionality.

---

## Overview of the ARISE Prediction UI

The ARISE Prediction landing page is designed to help users predict resource usage and execution time for AI workloads based on historical data or performance benchmarks. The UI includes:

- Input configuration options.
- Customizable output parameters.
- Filtering tools for better result analysis.

---

## Key Sections

- **Prediction Configuration Panel:**  
  Located in the left sidebar, this panel allows users to define input parameters, output fields, and other configurations required for the prediction process. It also includes the **Predict** button.

- **Input Configuration Panel:**  
  Enables the selection of input fields. Users can define numeric or categorical fields and set ranges or values to specify the prediction space.

- **Output Configuration Panel:**  
  Allows the selection of output fields to determine the desired prediction metrics.

- **Main Display Area:**  
  Displays prediction results and supports additional interactions.

- **Interactive Query Panel:**  
  Found at the bottom right, this AI Bot lets users ask questions or explore additional features.

---

## Configuring Input Parameters

Input parameters are set in the **Prediction Configuration Panel** and are essential for accurate results. The available fields depend on the dataset and model used. Below are the configurable input parameters for the `MLCommons` dataset:

1. **Number of Accelerators:**  
   - **Purpose:** Define the number and type of GPUs or accelerators to use.  
   - **Configuration:** Use the slider to select the number of accelerators (range: 08).

2. **Number of Nodes:**  
   - **Purpose:** Specify the number of compute nodes.  
   - **Configuration:** Adjust the slider (range: 14).

3. **Accelerator Type:**  
   - **Purpose:** Select the type of accelerator.  
   - **Configuration:** Use the multi-select dropdown for supported models, such as NVIDIA H100.

4. **Host Processor Core Count:**  
   - **Purpose:** Specify the number of CPU cores available on the host system.  
   - **Configuration:** Adjust the slider (range: 0128).

5. **Model MLC:**  
   - **Purpose:** Select the AI model being evaluated.  
   - **Configuration:** Use the dropdown to choose a model, e.g., `llama2-70b`.

6. **Processor Type:**  
   - **Purpose:** Define the processor type for computations.  
   - **Configuration:** Choose from available options, such as Intel Xeon or AMD EPYC.

7. **Scenario:**  
   - **Purpose:** Define the workload scenario.  
   - **Configuration:** Select options like *Offline* or *Server*.

---

## Configuring Output Parameters

The **Output Configuration Panel** allows users to select prediction metrics. For the `MLCommons` dataset, available outputs include:

1. **Tokens Per Second:**  
   - **Purpose:** Display the model's token generation rate based on the configuration.  
   - **Configuration:** Check the box next to this metric.

> **Note:** Multiple outputs can be selected for a comprehensive analysis.

---

## Interpreting the Results Table

After configuring inputs and outputs, click the **Predict** button. Results appear in the **Main Display Area**. For the `MLCommons` dataset, the table includes:

- **Resource Estimation:** Expected hardware and node usage.
- **Performance Metrics:** Metrics like tokens per second.
- **Scenario Details:** A summary of input configurations.

### Example Table:

| Metric               | Value         |
|-----------------------|---------------|
| Tokens Per Second     | 4500          |
| Accelerators Used     | 3             |
| Accelerator           | NVIDIA H100   |
| CPU Cores             | 42            |

---

## Using Filters for Analysis

The result table includes filtering features to refine results:

- **Sort by Metric:**  
  Organize data based on performance or resource usage, either ascending or descending.

- **Dropdown Filters:**  
  Refine results based on categories (e.g., accelerator type) or numerical ranges (e.g., tokens per second).  

### How to Use:
1. Click the **Add Filters** button to open a filter selection combo box.
2. Select the column to filter.
3. Use the dropdown or slider to narrow the data focus.

---

## Example Use Case

**Scenario:** Estimate the resources required to achieve 5000 tokens per second for an AI model using NVIDIA H100 GPUs.

### Steps:

1. Open the ARISE Prediction page.
2. Configure the following inputs:
   - **Accelerators:** 3  
   - **Nodes:** 1  
   - **Accelerator Type:** NVIDIA H100  
   - **Host Processor Core Count:** 42  
   - **Model MLC:** llama2-70b  
   - **Processor:** Intel Xeon  
   - **Scenario:** Server  
3. Configure the following outputs:
   - **Tokens Per Second:** Select this output field.  
4. Click **Predict**.

### Review the Results:

1. The table displays the predicted tokens per second (e.g., 4500) and other metrics like resource usage.
2. Click **Add Filters**.  
3. Select **Tokens Per Second**.  
4. Use the slider to focus on values near 5000 tokens per second.

---

## Notes and Recommendations

- **Model Training:** Ensure the prediction model is pre-trained on workload data for accurate results.  
- **Patience:** Predictions may take time based on the complexity of configurations.  
- **Iterative Adjustments:** Experiment with inputs to explore how different configurations impact performance.
