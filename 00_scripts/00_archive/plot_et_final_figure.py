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

# -----------------------------
# NORTH ARROW
# -----------------------------
def add_north_arrow(ax, size=0.08):
    ax.annotate(
        'N',
        xy=(0.08, 0.92), xytext=(0.08, 0.75),
        xycoords='axes fraction',
        arrowprops=dict(facecolor='black', width=3, headwidth=8),
        ha='center', va='center', fontsize=12, fontweight='bold'
    )


# -----------------------------
# SCALE BAR (km)
# -----------------------------
def add_scalebar(ax, pixel_size_km=0.03, length_km=20):
    """
    pixel_size_km = raster resolution in km (30 m = 0.03 km)
    length_km     = scale bar length
    """

    length_px = length_km / pixel_size_km

    x_start = ax.get_xlim()[0] + 0.05*(ax.get_xlim()[1]-ax.get_xlim()[0])
    y_start = ax.get_ylim()[0] + 0.05*(ax.get_ylim()[1]-ax.get_ylim()[0])

    ax.plot([x_start, x_start+length_px], [y_start, y_start],
            color='black', linewidth=3)

    ax.text(x_start + length_px/2, y_start + 15,
            f"{length_km} km",
            ha='center', fontsize=10, fontweight='bold')
            
fp_path  = os.path.join(indices_dir, f"ET24_{date}_{hour}_{region}.tif")
ref_path = os.path.join(indices_dir, f"ET24_final_{date}_{hour}_{region}.tif")

ET24_fp, nodata = read_raster(fp_path)
ET24_ref, _     = read_raster(ref_path)

if nodata is None:
    nodata = -9999.0


# -----------------------------
# COMPUTE DIFFERENCE
# -----------------------------
mask = (ET24_fp > nodata) & (ET24_ref > nodata)

ET24_diff = np.full_like(ET24_fp, nodata)
ET24_diff[mask] = ET24_ref[mask] - ET24_fp[mask]

fp_plot   = np.where(mask, ET24_fp, np.nan)
ref_plot  = np.where(mask, ET24_ref, np.nan)
diff_plot = np.where(mask, ET24_diff, np.nan)

fp_vals   = ET24_fp[mask]
ref_vals  = ET24_ref[mask]
diff_vals = ET24_diff[mask]


# -----------------------------
# SAMPLE for histograms (stable)
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
# PLOT FULL FIGURE
# -----------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 9))

# ---- MAPS (TOP ROW) ----
im1 = axes[0,0].imshow(fp_plot)
axes[0,0].set_title("First-pass ET")
axes[0,0].axis("off")
plt.colorbar(im1, ax=axes[0,0], fraction=0.046)
# add north arrow (first map)
add_north_arrow(axes[0,0])

# add scale bar (middle map)
add_scalebar(axes[0,1], pixel_size_km=0.03, length_km=20)

im2 = axes[0,1].imshow(ref_plot)
axes[0,1].set_title("Refined ET")
axes[0,1].axis("off")
plt.colorbar(im2, ax=axes[0,1], fraction=0.046)

im3 = axes[0,2].imshow(diff_plot, cmap="RdBu")
axes[0,2].set_title("ET Difference")
axes[0,2].axis("off")
plt.colorbar(im3, ax=axes[0,2], fraction=0.046)


# ---- HISTOGRAMS (BOTTOM ROW) ----
axes[1,0].hist(fp_vals, bins=50)
axes[1,0].set_title("Histogram: First-pass ET")
axes[1,0].set_xlabel("ET (mm day⁻¹)")
axes[1,0].set_ylabel("Frequency")
axes[1,0].grid(alpha=0.3)

axes[1,1].hist(ref_vals, bins=50)
axes[1,1].set_title("Histogram: Refined ET")
axes[1,1].set_xlabel("ET (mm day⁻¹)")
axes[1,1].set_ylabel("Frequency")
axes[1,1].grid(alpha=0.3)

axes[1,2].hist(diff_vals, bins=50)
axes[1,2].set_title("Histogram: Difference")
axes[1,2].set_xlabel("ET difference (mm day⁻¹)")
axes[1,2].set_ylabel("Frequency")
axes[1,2].grid(alpha=0.3)


plt.tight_layout()

out_path = os.path.join(fig_dir, "ET_final_full_comparison.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved:", out_path)