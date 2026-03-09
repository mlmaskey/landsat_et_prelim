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

## Quick Start

Follow these steps to run the SEBAL workflow from scratch.

### Step 1 — Clone Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### Step 2 — Create Environment

```bash
conda env create -f sebal_env.yml
conda activate sebal_dl
```

### Step 3 — Launch Jupyter

```bash
jupyter lab
```

### Step 4 — Run Workflow (Recommended Order)

Run scripts/notebooks in the following order:

1. Prepare raw Landsat data → `01_raw_landsat/`  
2. Mosaic scenes → `02_merge_landsat/`  
3. Clip to AOI → `03_clip_landsat/`  
4. Process meteorological data → `03_processed_met/`  
5. Compute SEBAL indices → `04_indices/`  
6. Generate maps and plots → `05_visuals/`

### Step 5 — Check Outputs

Final outputs will be saved in:

• `04_indices/` → SEBAL results  
• `05_visuals/` → figures and maps


## 📖 Citation

Please cite:

**APA style**

Maskey, M. L. (2026). *Landsat ET preliminary workflow: SEBAL-based evapotranspiration processing*. GitHub repository. [https://github.com/your-username/your-repo-name](https://github.com/mlmaskey/landsat_et_prelim)

**BibTeX**

```bibtex
@misc{maskey2026sebal,
  author       = {Maskey, Mahesh Lal},
  title        = {Landsat ET Preliminary Workflow: SEBAL-Based Evapotranspiration Processing},
  year         = {2026},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  url          = {[https://github.com/your-username/your-repo-name](https://github.com/mlmaskey/landsat_et_prelim/}
}
```

**Suggested acknowledgement**

> This workflow builds on the Surface Energy Balance Algorithm for Land (SEBAL) framework and is intended for research and educational applications in evapotranspiration estimation.
