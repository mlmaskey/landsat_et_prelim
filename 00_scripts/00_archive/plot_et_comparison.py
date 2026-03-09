import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt


def read_raster(path: str):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        nodata = src.nodata
    return arr, nodata


def get_valid_mask(*arrays, nodata=-9999.0):
    mask = np.ones(arrays[0].shape, dtype=bool)
    for arr in arrays:
        mask &= np.isfinite(arr)
        mask &= arr > nodata
    return mask


def plot_map(arr, title, out_path, nodata=-9999.0):
    valid = arr > nodata
    data = np.where(valid, arr, np.nan)

    plt.figure(figsize=(7, 5))
    im = plt.imshow(data)
    plt.colorbar(im, label=title)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_histogram(values, title, xlabel, out_path, max_sample=100000):
    if values.size == 0:
        print(f"Skipped histogram for {title}: no valid data")
        return

    if values.size > max_sample:
        rng = np.random.default_rng(42)
        idx = rng.choice(values.size, size=max_sample, replace=False)
        values = values[idx]

    plt.figure(figsize=(6, 4))
    plt.hist(values, bins=50)
    plt.xlabel(xlabel)
    plt.ylabel("Pixel count")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def print_stats(name, values):
    print(f"\n{name}")
    print(f"Min:    {float(np.min(values)):.4f}")
    print(f"Max:    {float(np.max(values)):.4f}")
    print(f"Mean:   {float(np.mean(values)):.4f}")
    print(f"Median: {float(np.median(values)):.4f}")
    for p in [1, 5, 25, 50, 75, 95, 99]:
        print(f"{p:>2}%:    {float(np.percentile(values, p)):.4f}")


def main():
    base_dir = r"G:\Collaborations\Mentee\UF_Anitha Madapakula\Scripts\Python\SEBAL_20200119_MSDelta"
    indices_dir = os.path.join(base_dir, "04_indices")
    fig_dir = os.path.join(base_dir, "plots_et_comparison")
    os.makedirs(fig_dir, exist_ok=True)

    date = "20200119"
    hour = "16Z"
    region = "MSDelta"

    et24_fp_path = os.path.join(indices_dir, f"ET24_{date}_{hour}_{region}.tif")
    et24_ref_path = os.path.join(indices_dir, f"ET24_final_{date}_{hour}_{region}.tif")
    etinst_fp_path = os.path.join(indices_dir, f"ETinst_{date}_{hour}_{region}.tif")
    etinst_ref_path = os.path.join(indices_dir, f"ETinst_final_{date}_{hour}_{region}.tif")
    ef_ref_path = os.path.join(indices_dir, f"EF_final_{date}_{hour}_{region}.tif")

    et24_fp, nodata1 = read_raster(et24_fp_path)
    et24_ref, nodata2 = read_raster(et24_ref_path)
    etinst_fp, nodata3 = read_raster(etinst_fp_path)
    etinst_ref, nodata4 = read_raster(etinst_ref_path)
    ef_ref, nodata5 = read_raster(ef_ref_path)

    nodata = -9999.0
    if nodata1 is not None:
        nodata = nodata1

    valid_et24 = get_valid_mask(et24_fp, et24_ref, nodata=nodata)
    et24_diff = np.full(et24_fp.shape, nodata, dtype="float32")
    et24_diff[valid_et24] = et24_ref[valid_et24] - et24_fp[valid_et24]

    valid_etinst = get_valid_mask(etinst_fp, etinst_ref, nodata=nodata)
    etinst_diff = np.full(etinst_fp.shape, nodata, dtype="float32")
    etinst_diff[valid_etinst] = etinst_ref[valid_etinst] - etinst_fp[valid_etinst]

    plot_map(et24_fp, "First-pass ET24 (mm/day)", os.path.join(fig_dir, "ET24_firstpass.png"), nodata)
    plot_map(et24_ref, "Refined ET24 (mm/day)", os.path.join(fig_dir, "ET24_refined.png"), nodata)
    plot_map(et24_diff, "ET24 Difference (Refined - First-pass)", os.path.join(fig_dir, "ET24_difference.png"), nodata)

    plot_map(etinst_fp, "First-pass ETinst (mm/hr)", os.path.join(fig_dir, "ETinst_firstpass.png"), nodata)
    plot_map(etinst_ref, "Refined ETinst (mm/hr)", os.path.join(fig_dir, "ETinst_refined.png"), nodata)
    plot_map(etinst_diff, "ETinst Difference (Refined - First-pass)", os.path.join(fig_dir, "ETinst_difference.png"), nodata)

    plot_map(ef_ref, "Refined EF (-)", os.path.join(fig_dir, "EF_refined.png"), nodata)

    et24_diff_vals = et24_diff[et24_diff > nodata]
    etinst_diff_vals = etinst_diff[etinst_diff > nodata]

    plot_histogram(
        et24_diff_vals,
        "Histogram of ET24 Difference",
        "ET24 difference (mm/day)",
        os.path.join(fig_dir, "hist_ET24_difference.png"),
    )

    plot_histogram(
        etinst_diff_vals,
        "Histogram of ETinst Difference",
        "ETinst difference (mm/hr)",
        os.path.join(fig_dir, "hist_ETinst_difference.png"),
    )

    print_stats("ET24 Difference (mm/day)", et24_diff_vals)
    print_stats("ETinst Difference (mm/hr)", etinst_diff_vals)

    print(f"\nAll figures saved in: {fig_dir}")


if __name__ == "__main__":
    main()