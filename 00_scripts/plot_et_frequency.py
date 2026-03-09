import numpy as np
import matplotlib.pyplot as plt
import os
from Utility import read_raster

# -----------------------
# Paths
# -----------------------
indices_dir = "../04_indices"
out_dir = "../05_visuals"

date = "20200119"
hour_tag = "16Z"
region = "MSDelta"

os.makedirs(out_dir, exist_ok=True)

# -----------------------
# Read rasters
# -----------------------
ET24_fp_path   = os.path.join(indices_dir, f"ET24_firstpass_{date}_{hour_tag}_{region}.tif")
ET24_ref_path  = os.path.join(indices_dir, f"ET24_refined_{date}_{hour_tag}_{region}.tif")
ETinst_fp_path = os.path.join(indices_dir, f"ETinst_firstpass_{date}_{hour_tag}_{region}.tif")
ETinst_ref_path= os.path.join(indices_dir, f"ETinst_refined_{date}_{hour_tag}_{region}.tif")

ET24_fp, _, _    = read_raster(ET24_fp_path)
ET24_ref, _, _   = read_raster(ET24_ref_path)
ETinst_fp, _, _  = read_raster(ETinst_fp_path)
ETinst_ref, _, _ = read_raster(ETinst_ref_path)

# -----------------------
# Common valid mask
# -----------------------
valid = (
    (ET24_fp > -9999) & (ET24_ref > -9999) &
    (ETinst_fp > -9999) & (ETinst_ref > -9999)
)

daily_diff  = ET24_ref[valid]   - ET24_fp[valid]
hourly_diff = ETinst_ref[valid] - ETinst_fp[valid]

print("Hourly mean/std:", float(np.mean(hourly_diff)), float(np.std(hourly_diff)))
print("Daily  mean/std:", float(np.mean(daily_diff)), float(np.std(daily_diff)))

# -----------------------
# Better x-limits
# -----------------------
# Hourly is very tight, so zoom using percentiles
h_lo = np.percentile(hourly_diff, 0.5)
h_hi = np.percentile(hourly_diff, 99.5)

# Daily has broader spread
d_lo = np.percentile(daily_diff, 0.5)
d_hi = np.percentile(daily_diff, 99.5)

# -----------------------
# Plot
# -----------------------
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

# Hourly
ax[0].hist(hourly_diff, bins=50, edgecolor="black", linewidth=0.4)
ax[0].axvline(0, linestyle="--", linewidth=1.2, color="red")
ax[0].set_title("Hourly Difference (ETinst)")
ax[0].set_xlabel("ET Difference (mm/hr)")
ax[0].set_ylabel("Frequency")
ax[0].set_xlim(h_lo, h_hi)
ax[0].grid(alpha=0.3)

# Daily
ax[1].hist(daily_diff, bins=50, edgecolor="black", linewidth=0.4)
ax[1].axvline(0, linestyle="--", linewidth=1.2, color="red")
ax[1].set_title("Daily Difference (ET24)")
ax[1].set_xlabel("ET Difference (mm/day)")
ax[1].set_xlim(d_lo, d_hi)
ax[1].grid(alpha=0.3)

plt.tight_layout()

fig_path = os.path.join(out_dir, f"ET_diff_sidebyside_better_{date}_{hour_tag}_{region}.png")
plt.savefig(fig_path, dpi=300, bbox_inches="tight")

print("Saved figure:", fig_path)