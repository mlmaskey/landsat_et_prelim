import os
import glob
import requests
import shutil
import urllib.request
import tarfile
from pystac_client import Client
import planetary_computer as pc
import datetime
import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
import rioxarray as rxr
import rasterio
from rasterio.mask import mask
from rasterio.merge import merge

def getscenes(bbox, scenes, date):
    # connect to the Microsoft Planetary Computer STAC catalog to search and access satellite datasets (including Landsat)
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    # search Landsat Collection-2 Level-2 scenes within the Mississippi Delta bounding box for 19 Jan 2020
    search = catalog.search(collections=scenes, bbox=bbox, datetime=f"{date}/{date}")
    # convert the filtered search results into a list of Landsat scene metadata
    items = list(search.items())
    # check how many Landsat scenes were found for the study area and date
    if len(items)>0:
        print(f"Number of set for the given box on {date}: {len(items)}")
        # display the scene ID of the first Landsat image found
        print (f"Scene scene ID of the first Landsat image {items[0].id}")
        # list all Landsat scene IDs covering the study area for this date
        print ("List of all scenes:")
        for item in items: print(item.id)
    else:
        print (f"No scenes are available for {date}")
        return []
        
    return items

def get_link(item, band_name):
    # sign the scene item to attach a temporary access token (required to download from the storage account)
    signed_item = pc.sign(item)
    # get the signed (authorized) download URL for the red band
    band_url  = signed_item.assets[band_name].href
    print (band_url)
    return band_url

def download_scene(band_url, dir2save):
    
    # extract the real filename by removing the security token from the signed URL
    filename = os.path.basename(band_url.split("?")[0])

    # verify the extracted Landsat band file name
    print(f"Extracted Landsat band file name: {filename}")

    # create the full local file path where the band will be saved
    file_out = os.path.join(dir2save, filename)

    # download the GeoTIFF from the cloud and save it locally
    urllib.request.urlretrieve(band_url, file_out)

    print(f"Downloaded as {file_out}")

    return file_out


def get_file_dataframe(filepath, preview_rows=10):
    """
    Read the CSV of downloaded Landsat files and return:
      band_files (dict): {band_name: file_path} for the selected scene
      scene (str): selected scene_id
      df (DataFrame): full table
    You can select a scene by:
      - scene_id="LE07_L2SP_023036_20200119_02_T1"
      - scene_index=1
    """
    df = pd.read_csv(filepath)
    
    scenes = sorted(df["scene_id"].unique())

    # print(f"\n--- Landsat download table (first {preview_rows} rows) ---")
    print(df.head(preview_rows))

    print("\n--- Available scenes ---")
    for s in scenes:
        print(s)

    bands = sorted(df["band"].unique())

    band_files = {}
    
    print("\n--- Files per band ---")
    for b in bands:
        files = df[df["band"] == b]["file"].tolist()
        band_files[b] = files

        print(f"{b:8s} -> {len(files)} files")
        
    return band_files, scenes, df

def get_file_dataframe_v1(filepath, scene_id=None, scene_index=None, preview_rows=10):
    """
    Read the CSV of downloaded Landsat files and return:
      band_files (dict): {band_name: file_path} for the selected scene
      scene (str): selected scene_id
      df (DataFrame): full table
    You can select a scene by:
      - scene_id="LE07_L2SP_023036_20200119_02_T1"
      - scene_index=1
    """
    df = pd.read_csv(filepath)

    # print(f"\n--- Landsat download table (first {preview_rows} rows) ---")
    # print(df.head(preview_rows))

    scenes = sorted(df["scene_id"].unique())
    print("\n--- Available scenes ---")
    for i, s in enumerate(scenes):
        print(f"{i}: {s}")

    # Decide which scene to use
    if scene_id is not None:
        if scene_id not in scenes:
            raise ValueError(f"scene_id not found: {scene_id}\nAvailable: {scenes}")
        scene = scene_id
    elif scene_index is not None:
        if not (0 <= scene_index < len(scenes)):
            raise ValueError(f"scene_index out of range: {scene_index} (0..{len(scenes)-1})")
        scene = scenes[scene_index]
    else:
        scene = scenes[0]  # default: first scene

    print(f"\n--- Using scene: {scene} ---")

    scene_df = df[df["scene_id"] == scene].copy()

    # print("\n--- Bands available for this scene ---")
    # print(scene_df[["band", "file"]].sort_values("band").to_string(index=False))

    # build band -> file dictionary
    band_files = dict(zip(scene_df["band"], scene_df["file"]))

    print("\n--- band_files dictionary ---")
    for b in sorted(band_files.keys()):
        print(f"{b:8s} -> {band_files[b]}")

    return band_files, scene, df


def get_aoi(shape_file): 
    aoi = gpd.read_file(shape_file)
    print("MSDelta CRS:", aoi.crs)
    print("MSDelta bounds:", aoi.total_bounds)  # [minx, miny, maxx, maxy]
    aoi.head()
    # Convert polygon to geometry format used by rasterio
    aoi_geom = [aoi.geometry.iloc[0]]
    print("Geometry ready for raster masking.")
    return aoi, aoi_geom

def get_band (band_dict, band_name):
    band_path = band_dict[band_name]
    src = rasterio.open(band_path)
    print("Raster CRS:", src.crs)
    print("Raster bounds:", src.bounds)
    print("Test band:", band_name)
    print("dtype:", src.dtypes[0], "nodata:", src.nodata)
    return src

    
def get_clip (src, aoi_geom, crop=True):
    # clip to MS Delta polygon
    clipped, clipped_transform = mask(src, aoi_geom, crop=crop)
    clipped_meta = src.meta.copy()
    # update metadata for the clipped raster
    clipped_meta.update({
        "height": clipped.shape[1],
        "width": clipped.shape[2],
        "transform": clipped_transform
    })
    print("Original shape:", (src.height, src.width))
    print("Clipped shape:", (clipped.shape[1], clipped.shape[2]))
    print("CRS:", src.crs)
    src.close()
    return clipped, clipped_meta


def save_clipped(src, aoi_geom, out_dir, band_name, scene, crop):
    clipped, clipped_meta = get_clip (src, aoi_geom, crop=crop)
    # make sure folder exists
    os.makedirs(out_dir, exist_ok=True)
    out_tif = f"{out_dir}/{band_name}_{scene}_MSDelta.tif"
    for f in glob.glob(out_tif):
        try:
            os.remove(f)
            print("Deleted:", f)
        except Exception as e:
            print("Could NOT delete:", f, "|", e)
    dst = rasterio.open(out_tif, "w", **clipped_meta)
    dst.write(clipped)   # <-- THIS is the raster array
    dst.close()
    print("Saved:", out_tif)
    return dst

def check_info(out_dir, band_name, scene):
    check_tif = f"{out_dir}/{band_name}_{scene}_MSDelta.tif"
    ds = rasterio.open(check_tif)
    print("Opened:", check_tif)
    print("CRS:", ds.crs)
    print("Bounds:", ds.bounds)
    print("Shape:", (ds.height, ds.width), "Count:", ds.count)
    print("Dtype:", ds.dtypes[0], "Nodata:", ds.nodata)
    ds.close()
    return ds

def save_mosiac(merge_dir, band_dict, scenes, band):
    """
    Create a mosaic for a given Landsat band across multiple scenes.

    This function opens all source rasters for the selected band, merges them
    into a single mosaic using rasterio.merge, and writes the output GeoTIFF
    to the specified directory. Existing mosaic files are safely overwritten.

    Parameters
    ----------
    merge_dir : str
        Directory where the mosaic GeoTIFF will be saved.
    band_dict : dict
        Dictionary mapping band names to lists of source raster file paths.
    scenes : list
        List of Landsat scene IDs (used to extract acquisition date).
    band : str
        Target band name (e.g., "blue", "red", "nir").

    Returns
    -------
    mosaic_path : str
        File path to the saved mosaic raster.
    """
    os.makedirs(merge_dir, exist_ok=True)

    src_files = band_dict[band]
    srcs = [rasterio.open(fp) for fp in src_files]

    try:
        mosaic, out_transform = merge(srcs)

        meta = srcs[0].meta.copy()
        meta.update({
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_transform,
            "count": mosaic.shape[0]
        })

        date = scenes[0].split("_")[3]
        mosaic_path = os.path.join(merge_dir, f"{band}_{date}_mosaic.tif")

        if os.path.exists(mosaic_path):
            os.remove(mosaic_path)

        with rasterio.open(mosaic_path, "w", **meta) as dst:
            dst.write(mosaic)

        print("Saved mosaic:", mosaic_path)
        return mosaic_path

    finally:
        for s in srcs:
            s.close()

def load_rasters(file, clip_dir, bands):
    """
    Load clipped Landsat bands automatically for SEBAL processing.

    Parameters
    ----------
    file : str
        CSV file listing downloaded Landsat scenes (landsat_downloaded_files.csv)

    clip_dir : str
        Folder containing clipped Landsat bands (e.g., 03_clip_landsat)

    bands : list
        List of band names to load (e.g., ["blue","green","red","nir08","swir16","swir22","lwir"])

    Returns
    -------
    rasters : dict
        Dictionary of raster arrays indexed by band name

    srcs : dict
        Dictionary of rasterio dataset objects (used later for metadata/saving outputs)

    date : str
        Acquisition date extracted automatically from scene ID
    """

    # Get scene list from CSV
    band_dict, scenes, df = get_file_dataframe(file)

    # Extract date automatically from first scene
    date = scenes[0].split("_")[3]
    print("Date:", date)

    rasters = {}
    srcs = {}

    # Load each band automatically
    for b in bands:
        path = f"{clip_dir}/{b}_{date}_MSDelta.tif"
        src = rasterio.open(path)

        rasters[b] = src.read(1)
        srcs[b] = src

    print("Loaded bands:", list(rasters.keys()))
    print("Example shape (red):", rasters["red"].shape)
    return rasters, srcs, date


def calculate_NDVI(rasters):
    """
    Compute NDVI from Landsat rasters.

    Parameters
    ----------
    rasters : dict
        Dictionary containing Landsat bands (must include 'red' and 'nir08').

    Returns
    -------
    ndvi : ndarray (float32)
        NDVI raster with nodata = -9999
    """

    red_raw = rasters["red"].astype("float32")
    nir_raw = rasters["nir08"].astype("float32")

    # Define valid pixels for NDVI calculation.
    # Landsat Collection-2 SR bands are first converted to surface reflectance.
    # We exclude:
    #   (1) nodata/invalid reflectance values (reflectance < -0.2 after scaling),
    #   (2) numerically unstable pixels where (red + nir) ≈ 0, which can produce extreme NDVI.
    # No additional reflectance clipping is applied to preserve physically meaningful values.
    red = red_raw * 0.0000275 - 0.2
    nir = nir_raw * 0.0000275 - 0.2

    # Valid pixels:
    valid = (
        (red > 0.0) & (red <= 1.0) &
        (nir > 0.0) & (nir <= 1.0) &
        (np.abs(red + nir) > 0.0001)
    )    
    
    # Initialize NDVI with nodata
    ndvi = np.full(red.shape, -9999.0, dtype=np.float32)

    # NDVI formula
    ndvi[valid] = (nir[valid] - red[valid]) / (nir[valid] + red[valid])

    # Quick diagnostics
    print("NDVI min/max (valid):", float(ndvi[valid].min()), float(ndvi[valid].max()))
    print("NDVI nodata count:", int((ndvi == -9999.0).sum()))
    return ndvi
    
def calculate_albedo(rasters):
    """
    Compute broadband surface albedo (Landsat-style approximation).

    Returns
    -------
    albedo : ndarray (float32)
        Albedo raster with nodata = -9999
    """

    blue  = rasters["blue"]
    red   = rasters["red"]
    nir   = rasters["nir08"]
    swir1 = rasters["swir16"]
    swir2 = rasters["swir22"]

    # valid pixels: exclude nodata=0 and avoid weird zeros
    valid = (blue > 0) & (red > 0) & (nir > 0) & (swir1 > 0) & (swir2 > 0)

    albedo = np.full(red.shape, -9999.0, dtype=np.float32)

    # broadband albedo approximation
    albedo[valid] = (
        0.356 * blue[valid]
        + 0.130 * red[valid]
        + 0.373 * nir[valid]
        + 0.085 * swir1[valid]
        + 0.072 * swir2[valid]
        - 0.0018
    )

    print("Albedo min/max (valid):", float(albedo[valid].min()), float(albedo[valid].max()))
    print("Albedo nodata count:", int((albedo == -9999.0).sum()))    

    return albedo


def clip_save_aorc_var(ncfile, ref_tif, out_tif, aorc_var, nodata_out=-9999.0):

    # 1) open AORC
    ds = xr.open_dataset(ncfile)
    da = ds[aorc_var]

    # 2) set spatial dims (AORC uses lon/lat)
    da = da.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=False)

    # 3) CRS: set only if missing (assume WGS84 lon/lat)
    if da.rio.crs is None:
        da = da.rio.write_crs("EPSG:4326", inplace=False)

    # 4) open reference raster (Landsat grid)
    ref = rxr.open_rasterio(ref_tif).squeeze()

    # 5) reproject to match Landsat exactly
    da_match = da.rio.reproject_match(ref)

    # 6) mask using ref footprint (no extra mask file)
    ref_nodata = ref.rio.nodata
    valid = xr.ones_like(ref, dtype=bool)

    if ref_nodata is not None:
        valid = valid & (ref != ref_nodata)

    valid = valid & xr.ufuncs.isfinite(ref)
    da_match = da_match.where(valid)

    # 7) save
    da_match.rio.to_raster(out_tif, nodata=nodata_out)

    print("Saved:", out_tif, "shape:", da_match.shape, "var:", aorc_var)
    return out_tif


def clip_save_met_var(raw_met_dir, landsat_dir, proc_dir, date, hour, region, aorc_var, out_name):
    ncfile  = os.path.join(raw_met_dir, f"aorc_full_{date}{hour}z.nc")
    ref_tif = os.path.join(landsat_dir, f"red_{date}_{region}.tif")
    out_tif = os.path.join(proc_dir, f"{out_name}_{date}_{hour}Z_{region}.tif")
    out_tif  = clip_save_aorc_var(ncfile, ref_tif, out_tif, aorc_var)
    return out_tif

def extract_mask_mean(raster_path, mask_path):
    with rasterio.open(raster_path) as r, rasterio.open(mask_path) as m:
        raster = r.read(1)
        mask = m.read(1)

        valid = (mask == 1) & (raster != r.nodata)
        return np.nanmean(raster[valid])

def read_raster(raster_path):
    # open raster
    src = rasterio.open(raster_path)

    # read band as float
    value = src.read(1).astype("float32")

    # copy metadata profile
    profile = src.profile.copy()

    # extract nodata
    nodata = src.nodata

    # close dataset
    src.close()

    # return only what we need
    return value, profile, nodata

def write_raster(raster_path, profile, value, ndata=-9999.0):

    # update profile
    profile.update(dtype="float32", nodata=ndata, count=1)

    # open output raster
    dst = rasterio.open(raster_path, "w", **profile)

    # write raster
    dst.write(value, 1)

    # close raster
    dst.close()

    print("Saved:", raster_path)

def check_raster(raster_path, name):

    # open raster
    src = rasterio.open(raster_path)

    # print shape + nodata
    print(f"{name} shape:", src.shape, "| nodata:", src.nodata)

    # close raster
    src.close()
