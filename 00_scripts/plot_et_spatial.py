import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from Utility import read_raster

# -----------------------
# Paths + settings
# -----------------------
indices_dir = "../04_indices"
out_dir = "../05_visuals"

date = "20200119"
hour_tag = "16Z"
region = "MSDelta"

os.makedirs(out_dir, exist_ok=True)

# -----------------------
# File paths
# -----------------------
ETinst_fp_path = os.path.join(indices_dir, f"ETinst_firstpass_{date}_{hour_tag}_{region}.tif")
ETinst_ref_path = os.path.join(indices_dir, f"ETinst_refined_{date}_{hour_tag}_{region}.tif")

ET24_fp_path = os.path.join(indices_dir, f"ET24_firstpass_{date}_{hour_tag}_{region}.tif")
ET24_ref_path = os.path.join(indices_dir, f"ET24_refined_{date}_{hour_tag}_{region}.tif")

# -----------------------
# Read rasters
# -----------------------
ETinst_fp, _, _ = read_raster(ETinst_fp_path)
ETinst_ref, _, _ = read_raster(ETinst_ref_path)

ET24_fp, _, _ = read_raster(ET24_fp_path)
ET24_ref, _, _ = read_raster(ET24_ref_path)

# -----------------------
# Convert nodata to NaN
# -----------------------
ETinst_fp = np.where(ETinst_fp > -9999, ETinst_fp, np.nan)
ETinst_ref = np.where(ETinst_ref > -9999, ETinst_ref, np.nan)

ET24_fp = np.where(ET24_fp > -9999, ET24_fp, np.nan)
ET24_ref = np.where(ET24_ref > -9999, ET24_ref, np.nan)

# -----------------------
# Shared color range by row
# -----------------------
hourly_vmin = float(np.nanmin([np.nanmin(ETinst_fp), np.nanmin(ETinst_ref)]))
hourly_vmax = float(np.nanmax([np.nanmax(ETinst_fp), np.nanmax(ETinst_ref)]))

daily_vmin = float(np.nanmin([np.nanmin(ET24_fp), np.nanmin(ET24_ref)]))
daily_vmax = float(np.nanmax([np.nanmax(ET24_fp), np.nanmax(ET24_ref)]))

print("Hourly min/max:", hourly_vmin, hourly_vmax)
print("Daily min/max :", daily_vmin, daily_vmax)

# -----------------------
# Figure layout
# -----------------------
fig = plt.figure(figsize=(11, 10))
gs = GridSpec(
    2, 3,
    width_ratios=[1, 1, 0.05],
    height_ratios=[1, 1],
    wspace=0.08,
    hspace=0.08
)

ax00 = fig.add_subplot(gs[0, 0])
ax01 = fig.add_subplot(gs[0, 1])
cax0 = fig.add_subplot(gs[0, 2])

ax10 = fig.add_subplot(gs[1, 0])
ax11 = fig.add_subplot(gs[1, 1])
cax1 = fig.add_subplot(gs[1, 2])

# -----------------------
# Top row: hourly
# -----------------------
im1 = ax00.imshow(ETinst_fp, vmin=hourly_vmin, vmax=hourly_vmax)
ax00.set_title("Hourly ETinst - First-pass")
ax00.axis("off")

im2 = ax01.imshow(ETinst_ref, vmin=hourly_vmin, vmax=hourly_vmax)
ax01.set_title("Hourly ETinst - Refined")
ax01.axis("off")

cbar0 = fig.colorbar(im2, cax=cax0)
cbar0.set_label("Hourly ET (mm/hr)")

# -----------------------
# Bottom row: daily
# -----------------------
im3 = ax10.imshow(ET24_fp, vmin=daily_vmin, vmax=daily_vmax)
ax10.set_title("Daily ET24 - First-pass")
ax10.axis("off")

im4 = ax11.imshow(ET24_ref, vmin=daily_vmin, vmax=daily_vmax)
ax11.set_title("Daily ET24 - Refined")
ax11.axis("off")

cbar1 = fig.colorbar(im4, cax=cax1)
cbar1.set_label("Daily ET (mm/day)")

# -----------------------
# Title + save
# -----------------------
fig.suptitle(f"SEBAL ET Spatial Maps ({date}, {hour_tag}, {region})", fontsize=18)

fig_path = os.path.join(out_dir, f"ET_maps_2x2_sidecolorbar_{date}_{hour_tag}_{region}.png")
plt.savefig(fig_path, dpi=300, bbox_inches="tight")

print("Saved figure:", fig_path)