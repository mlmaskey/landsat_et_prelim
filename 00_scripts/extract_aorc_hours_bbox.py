#!/usr/bin/env python3
"""
extract_aorc_hours.py  (REPLACED)

Now does: AORC v1.1 1km Zarr (AWS Open Data) -> Local hourly NetCDFs (download-only)

- Reads: s3://noaa-nws-aorc-v1-1-1km/<YEAR>.zarr  (anon)
- Time range is [start, end) unless --plus1hour (then includes end hour by +1h)
- Writes one NetCDF per hour into a FLAT output folder
- Includes full forcing vars needed for HRLDAS later:
    APCP, PRES, SPFH, TMP, UGRD, VGRD, DSWRF, DLWRF

This is NOT LDASIN conversion. It is the clean "download stage" for Option B.
"""

import os
import argparse
import numpy as np
import xarray as xr
import pandas as pd
from netCDF4 import Dataset


DEFAULT_AORC_VARS = [
    "APCP_surface",
    "DLWRF_surface",
    "DSWRF_surface",
    "PRES_surface",
    "SPFH_2maboveground",
    "TMP_2maboveground",
    "UGRD_10maboveground",
    "VGRD_10maboveground",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True, help="e.g., 2020")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD HH:MM:SS (UTC)")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD HH:MM:SS (UTC), end inclusive")
    ap.add_argument("--bbox", nargs=4, type=float, required=True,  metavar=("LON_MIN", "LON_MAX", "LAT_MIN", "LAT_MAX"),  help="WGS84 bbox in degrees: lon_min lon_max lat_min lat_max")
    ap.add_argument("--bbox-buffer-deg", type=float, default=0.05)
    ap.add_argument("--outdir", required=True, help="Output folder (flat) for hourly NetCDFs")
    ap.add_argument("--prefix", default="aorc_full", help="Output filename prefix")
    ap.add_argument("--vars", nargs="+", default=DEFAULT_AORC_VARS, help="Variables to download")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # --- read domain bbox (WGS84) from fulldom geometry ---
    # --- bbox from CLI (WGS84 degrees) ---
    minlon, maxlon, minlat, maxlat = args.bbox
    
    # apply buffer (same behavior as before)
    buf = float(args.bbox_buffer_deg)
    minlon -= buf
    maxlon += buf
    minlat -= buf
    maxlat += buf

    # --- time range ---
    t0 = pd.to_datetime(args.start)
    t1 = pd.to_datetime(args.end)
    if t1 <= t0:
        raise SystemExit("ERROR: end must be >= start (end is inclusive)")
    times = pd.date_range(t0, t1, freq="h", inclusive="both")

    # --- open Zarr (anon) ---
    zarr = f"s3://noaa-nws-aorc-v1-1-1km/{args.year}.zarr"
    ds = xr.open_zarr(zarr, consolidated=True, storage_options={"anon": True})

    missing = [v for v in args.vars if v not in ds]
    if missing:
        raise SystemExit(f"ERROR: Missing vars in Zarr: {missing}")

    ds = ds[args.vars]

    # --- spatial subset ---
    # Handle lon convention (0..360 vs -180..180)
    loncoord = ds["longitude"]
    lonmin = float(loncoord.min())
    use_0360 = (lonmin >= 0.0 and minlon < 0.0)

    if use_0360:
        minlon2 = (minlon + 360.0) % 360.0
        maxlon2 = (maxlon + 360.0) % 360.0
        ds_sp = ds.sel(longitude=slice(minlon2, maxlon2), latitude=slice(minlat, maxlat))
    else:
        ds_sp = ds.sel(longitude=slice(minlon, maxlon), latitude=slice(minlat, maxlat))

    print(f"[INFO] Zarr: {zarr}")
    print(f"[INFO] BBOX(WGS84+buf): lon[{minlon:.4f},{maxlon:.4f}] lat[{minlat:.4f},{maxlat:.4f}]")
    print(f"[INFO] Hours: {len(times)}  ({times[0]} -> {times[-1]})")
    print(f"[INFO] OUT: {args.outdir}")

    wrote = 0
    skipped = 0
    notfound_time = 0

    for t in times:
        stamp = t.strftime("%Y%m%d%H")
        out_path = os.path.join(args.outdir, f"{args.prefix}_{stamp}z.nc")

        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            skipped += 1
            continue

        try:
            d = ds_sp.sel(time=np.datetime64(t)).load()
        except Exception:
            notfound_time += 1
            continue

        d.attrs["source"] = zarr
        d.attrs["subset_bbox_wgs84_bufdeg"] = f"{minlon},{minlat},{maxlon},{maxlat}"
        d.to_netcdf(out_path, engine="scipy")
        wrote += 1

        if wrote <= 3 or wrote % 200 == 0:
            print(f"[OK] {os.path.basename(out_path)}")

    print("[DONE]")
    print(f"[SUMMARY] wrote={wrote} skipped_exists={skipped} time_missing={notfound_time}")


if __name__ == "__main__":
    main()
