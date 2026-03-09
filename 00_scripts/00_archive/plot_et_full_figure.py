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


# prepare arrays
fp_plot = np.where(mask, ET24_fp, np.nan)
ref_plot = np.where(mask, ET24_ref, np.nan)
diff_plot = np.where(mask, ET24_diff, np.nan)

diff_vals = ET24_diff[mask]
fp_vals = ET24_fp[mask]


# -----------------------------
# SAMPLE for histograms (safe)
# -----------------------------
rng = np.random.default_rng(42)

if diff_vals.size > 150000:
    diff_vals = rng.choice(diff_vals, size=150000, replace=False)

if fp_vals.size > 150000:
    fp_vals = rng.choice(fp_vals, size=150000, replace=False)


# -----------------------------
# FULL FIGURE
# -----------------------------
fig = plt.figure(figsize=(14, 9))

# ---- TOP ROW (maps) ----
ax1 = plt.subplot2grid((2,3),(0,0))
ax2 = plt.subplot2grid((2,3),(0,1))
ax3 = plt.subplot2grid((2,3),(0,2))

im1 = ax1.imshow(fp_plot)
ax1.set_title("First-pass ET (mm/day)")
ax1.axis("off")
plt.colorbar(im1, ax=ax1, fraction=0.046)

im2 = ax2.imshow(ref_plot)
ax2.set_title("Refined ET (mm/day)")
ax2.axis("off")
plt.colorbar(im2, ax=ax2, fraction=0.046)

im3 = ax3.imshow(diff_plot, cmap="RdBu")
ax3.set_title("Difference (Refined − First-pass)")
ax3.axis("off")
plt.colorbar(im3, ax=ax3, fraction=0.046)


# ---- BOTTOM ROW (histograms) ----
ax4 = plt.subplot2grid((2,3),(1,0), colspan=1)
ax5 = plt.subplot2grid((2,3),(1,1), colspan=2)

ax4.hist(fp_vals, bins=50)
ax4.set_title("Histogram: First-pass ET")
ax4.set_xlabel("ET (mm/day)")
ax4.set_ylabel("Pixel count")
ax4.grid(True, alpha=0.3)

ax5.hist(diff_vals, bins=50)
ax5.set_title("Histogram: Difference (Refined − First-pass)")
ax5.set_xlabel("ET difference (mm/day)")
ax5.set_ylabel("Pixel count")
ax5.grid(True, alpha=0.3)


plt.tight_layout()

out_path = os.path.join(fig_dir, "ET_full_comparison_figure.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved:", out_path)