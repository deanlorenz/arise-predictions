import pandas as pd
import matplotlib.pyplot as plt

from utils import constants, utils

from matplotlib.backends.backend_pdf import PdfPages

###
# Quick and dirty script to compare predictions against ground truth and plot.
###

# TODO read med predictions
# TODO plot med predictions and med actuals

# TODO read thpt predictions
# TODO plot thpt predictions and thpt actuals

predictions_med = "examples/inference_perf_eval/ARISE-auto-models/predictions-XGBoost-Regressor-med.csv"
predictions_thpt = "examples/inference_perf_eval/ARISE-auto-models/predictions-XGBoost-Regressor-thpt.csv"

# plot med predictions
predictions_med_df = pd.read_csv(predictions_med, low_memory=False)
print(f"predictions med original dtypes: {predictions_med_df.dtypes}")
print("\n")
print(f"predictions med head(10): {predictions_med_df.head(10)}")
predictions_med_filtered_df = predictions_med_df[
    (predictions_med_df["acc"] == "A100") & 
    (predictions_med_df["acc_count"] == 4) & 
    (predictions_med_df["back"] == "vllm") &
    (predictions_med_df["cpu"] == "IceLake") &
    (predictions_med_df["cpu_count"] == 128) &
    (predictions_med_df["dev"] == "cuda") &
    (predictions_med_df["ii"] == 128) &
    (predictions_med_df["mode"] == "base") &
    (predictions_med_df["model"] == "granite-13b") &
    (predictions_med_df["oo"] == 1024) &
    (predictions_med_df["prec"] == "fp16")
] 

print(f"Number rows predictions med after filtering: {len(predictions_med_filtered_df)}")
print(f"Filtered med predictions:\n {predictions_med_filtered_df[['bb', 'med']]}")
print("\n")

fig, ax = plt.subplots()
predictions_med_filtered_df.sort_values(by="bb").set_index("bb").plot(kind="line", y=["med", "prediction"] , ax=ax, grid=True, style=".-")
plt.show()

pdffig = PdfPages("med-predictions-vs-actual-subset-1.pdf")
fig.savefig(pdffig, format="pdf")

metadata = pdffig.infodict()
metadata["Filter"] = "acc: A100, acc_count: 1, back: vllm, cpu: IceLake, cpu_count: 128, dev: cuda, ii: 128, mode: base, model: granite-13b, oo: 1024, pred: fp16"
pdffig.close()

# plot thpt predictions
predictions_thpt_df = pd.read_csv(predictions_thpt, low_memory=False)
print(f"predictions thpt original dtypes: {predictions_thpt_df.dtypes}")
print("\n")
print(f"predictions thpt head(10): {predictions_thpt_df.head(10)}")
predictions_thpt_filtered_df = predictions_thpt_df[
    (predictions_thpt_df["acc"] == "A100") & 
    (predictions_thpt_df["acc_count"] == 4) & 
    (predictions_thpt_df["back"] == "vllm") &
    (predictions_thpt_df["cpu"] == "IceLake") &
    (predictions_thpt_df["cpu_count"] == 128) &
    (predictions_thpt_df["dev"] == "cuda") &
    (predictions_thpt_df["ii"] == 128) &
    (predictions_thpt_df["mode"] == "base") &
    (predictions_thpt_df["model"] == "granite-13b") &
    (predictions_thpt_df["oo"] == 1024) &
    (predictions_thpt_df["prec"] == "fp16")
] 

fig, ax = plt.subplots()
predictions_thpt_filtered_df.sort_values(by="bb").set_index("bb").plot(kind="line", y=["thpt", "prediction"] , ax=ax, grid=True, style=".-")
plt.show()

pdffig = PdfPages("thpt-predictions-vs-actual-subset-1.pdf")
fig.savefig(pdffig, format="pdf")

metadata = pdffig.infodict()
metadata["Filter"] = "acc: A100, acc_count: 1, back: vllm, cpu: IceLake, cpu_count: 128, dev: cuda, ii: 128, mode: base, model: granite-13b, oo: 1024, pred: fp16"
pdffig.close()

# utils.write_df_to_csv(df=predictions_med_filtered_df, output_path="examples/inference_perf_eval/debug", output_file="debug.csv")
