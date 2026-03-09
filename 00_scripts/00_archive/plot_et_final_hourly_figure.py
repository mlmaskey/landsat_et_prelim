import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt


# -----------------------------
# SETTINGS
# -----------------------------
base_dir = r"G:\Collaborations\Mentee\UF_Anitha Madapakula\Scripts\Python\SEBAL_20200119_MSDelta"
indices_dir = os.path.join(base_dir, "04_indices")
fig_dir = os.path.join(base_dir, "plots_et_hourly")
os.makedirs(fig_dir, exist_ok=True)

date = "20200119"
hour = "16Z"
region = "MSDelta"


# -----------------------------
# READ RASTERS
# -----------------------------
def read_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        nodata = src.nodata
    return arr, nodata


fp_path  = os.path.join(indices_dir, f"ETinst_{date}_{hour}_{region}.tif")
ref_path = os.path.join(indices_dir, f"ETinst_final_{date}_{hour}_{region}.tif")

ET_fp, nodata = read_raster(fp_path)
ET_ref, _     = read_raster(ref_path)

if nodata is None:
    nodata = -9999.0


# -----------------------------
# DIFFERENCE
# -----------------------------
mask = (ET_fp > nodata) & (ET_ref > nodata)

ET_diff = np.full_like(ET_fp, nodata)
ET_diff[mask] = ET_ref[mask] - ET_fp[mask]

fp_plot   = np.where(mask, ET_fp, np.nan)
ref_plot  = np.where(mask, ET_ref, np.nan)
diff_plot = np.where(mask, ET_diff, np.nan)

fp_vals   = ET_fp[mask]
ref_vals  = ET_ref[mask]
diff_vals = ET_diff[mask]


# -----------------------------
# SAMPLE histograms
# -----------------------------
rng = np.random.default_rng(42)

def sample_array(arr, n=150000):
    if arr.size > n:
        return rng.choice(arr, size=n, replace=False)
    return arr

fp_vals   = sample_array(fp_vals)
ref_vals  = sample_array(ref_vals)
diff_vals = sample_array(diff_vals)


# -----------------------------
# FIGURE
# -----------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 9))

# maps
im1 = axes[0,0].imshow(fp_plot)
axes[0,0].set_title("ETinst First-pass")
axes[0,0].axis("off")
plt.colorbar(im1, ax=axes[0,0], fraction=0.046)

im2 = axes[0,1].imshow(ref_plot)
axes[0,1].set_title("ETinst Refined")
axes[0,1].axis("off")
plt.colorbar(im2, ax=axes[0,1], fraction=0.046)

im3 = axes[0,2].imshow(diff_plot, cmap="RdBu")
axes[0,2].set_title("ETinst Difference")
axes[0,2].axis("off")
plt.colorbar(im3, ax=axes[0,2], fraction=0.046)


# histograms
axes[1,0].hist(fp_vals, bins=50)
axes[1,0].set_title("Histogram: ETinst First-pass")
axes[1,0].set_xlabel("ETinst")
axes[1,0].set_ylabel("Frequency")

axes[1,1].hist(ref_vals, bins=50)
axes[1,1].set_title("Histogram: ETinst Refined")
axes[1,1].set_xlabel("ETinst")

axes[1,2].hist(diff_vals, bins=50)
axes[1,2].set_title("Histogram: ETinst Difference")
axes[1,2].set_xlabel("Difference")

plt.tight_layout()

out_path = os.path.join(fig_dir, "ETinst_full_comparison.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved:", out_path)