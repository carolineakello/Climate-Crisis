# Flood Susceptibility Mapping (Humanised)

**What it does:** Combines simple factors (slope, distance to rivers, land cover, rainfall)
into one index showing where floods are more likely.

## Run
```bash
pip install -r requirements.txt
python mca.py
```

Open `susceptibility.tif` in QGIS. To use real data, replace the synthetic arrays
with rasters read from disk (ensure same resolution, CRS, and alignment).
