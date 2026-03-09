# Landsat ET Preliminary Workflow
This repository contains preliminary scripts for processing Landsat imagery and estimating evapotranspiration (ET) using a SEBAL-based workflow.  
It focuses on reproducible preprocessing, raster-based analysis, and visualization for regional-scale applications.

## Repository Structure

This repository follows a step-by-step workflow for Landsat-based SEBAL evapotranspiration processing, from raw data preparation to final visualization outputs.

### Folder Overview

- *00_scripts/*: Contains all Python scripts used in the workflow, including preprocessing, SEBAL calculations, and plotting routines.
- *00_shapefiles/* : Stores shapefiles defining the study area and masks used for clipping and spatial filtering.
- *01_raw_landsat/*: Holds original Landsat scenes exactly as downloaded. These files remain unchanged and serve as the primary data archive.
- *02_merge_landsat/*: Contains mosaicked Landsat scenes created when multiple tiles cover the study area.
- *02_raw_aorc/*: Includes raw AORC meteorological forcing data used for SEBAL energy balance calculations.
- *03_clip_landsat/*: Stores Landsat imagery clipped to the study area for efficient processing.
- *03_processed_met/*: Contains processed meteorological variables prepared for SEBAL modeling.
- *04_indices/*: Stores derived SEBAL outputs such as NDVI, albedo, LST, net radiation, soil heat flux, evaporative fraction, and evapotranspiration.
- *05_visuals/*: Contains maps, comparison plots, histograms, and other visualization outputs.
- *landsat_downloaded_files.csv*: Tracks downloaded Landsat scenes for documentation and reproducibility.

## Environment Setup (SEBAL Workflow)

This project uses a Conda environment to ensure reproducibility.

### Step 1: Install Conda

Install **Anaconda** or **Miniconda** if not already available.

### Step 2: Create Environment

### Step 4: Activate Environment

>> `conda env create -f sebal_env.yml`

### Step 5: Launch Jupyter Lab
>>  `jupyter lab`

