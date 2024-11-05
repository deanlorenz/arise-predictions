# ARISE in Action on Sample Data

To see ARISE in action on a sample dataset, we will use the [MLCommons example](../examples/MLCommons). This example
contains inference data from [MLCommons Datacenter Benchmark Results](https://mlcommons.org/benchmarks/inference-datacenter), 
where the inputs represent different configuration options of the GPU, LLM and environment, and the output is the 
measured throughput (tokens per second).

First, we will and run the `analyze-jobs` command, which generate descriptive statistics on the provided dataset. 

```bash
python src/main.py analyze-jobs --input-path examples/MLCommons
```

The output is written to a folder named `job-analysis` in the provided input path. `descriptive-stats.csv` file contains
general statistics about the dataset numeric inputs, such as min, max, mean and standard deviation. This file is 
accompanied by a PDF file containing box plots of same inputs, showing their ranges, distribution and outliers.   

For each output variable (in our example only `tokens_per_second`), a file named  `categorical-stats-<output_name>.csv` 
is created. For each combination of the categorical inputs, it computes the min, max, and mean of the output variable.

Finally, pearson correlations are computed between the different numeric variables. In our example, we can see that the
output `tokens_per_second` is moderately correlated (0.66) with the input `# of Accelartors`.

<img src="correlation-single-job.png"  width="60%" height="60%">