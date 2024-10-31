Inference data taken from  <https://mlcommons.org/benchmarks/inference-datacenter/>

The following modifications were applied to the downloaded data:

1. Removed duplicate columns
2. Filtered out rows for which the output is not in tokens/s units
3. Renamed the output columns from 'Avg. Result at System Name' to 'tokens_per_second'
4. Removed empty columns and columns with only one value 