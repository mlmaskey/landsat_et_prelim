import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt


# -----------------------------
# SETTINGS
# -----------------------------
base_dir = r"G:\Collaborations\Mentee\UF_Anitha Madapakula\Scripts\Python\SEBAL_20200119_MSDelta"
indices_dir = os.path.join(base_dir, "04_indices")
fig_dir = os.path.join(base_dir, "plots_et_comparison")
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


fp_path = os.path.join(indices_dir, f"ET24_{date}_{hour}_{region}.tif")
ref_path = os.path.join(indices_dir, f"ET24_final_{date}_{hour}_{region}.tif")

ET24_fp, nodata = read_raster(fp_path)
ET24_ref, _ = read_raster(ref_path)

if nodata is None:
    nodata = -9999.0

mask = (ET24_fp > nodata) & (ET24_ref > nodata)
ET24_diff = np.full_like(ET24_fp, nodata)
ET24_diff[mask] = ET24_ref[mask] - ET24_fp[mask]


# -----------------------------
# PREP DATA FOR PLOT
# -----------------------------
fp_plot = np.where(mask, ET24_fp, np.nan)
ref_plot = np.where(mask, ET24_ref, np.nan)
diff_plot = np.where(mask, ET24_diff, np.nan)


# -----------------------------
# SIDE-BY-SIDE FIGURE
# -----------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# first-pass
im1 = axes[0].imshow(fp_plot)
axes[0].set_title("First-pass ET (mm/day)")
axes[0].axis("off")
fig.colorbar(im1, ax=axes[0], fraction=0.046)

# refined
im2 = axes[1].imshow(ref_plot)
axes[1].set_title("Refined ET (mm/day)")
axes[1].axis("off")
fig.colorbar(im2, ax=axes[1], fraction=0.046)

# difference
im3 = axes[2].imshow(diff_plot, cmap="RdBu")
axes[2].set_title("Difference (Refined − First-pass)")
axes[2].axis("off")
fig.colorbar(im3, ax=axes[2], fraction=0.046)

plt.tight_layout()

out_path = os.path.join(fig_dir, "ET24_side_by_side.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved:", out_path)