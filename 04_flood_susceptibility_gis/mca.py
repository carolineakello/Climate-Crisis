"""
Flood Susceptibility Mapping — Multi‑Criteria (Humanised)
---------------------------------------------------------
Combine a few simple, made‑up rasters (slope, distance to river, land cover,
rainfall intensity) into one index map of "how susceptible to flooding"
each cell might be. Replace the generated rasters with your real inputs.
"""
import numpy as np
import rasterio
from rasterio.transform import from_origin

# 1) Create small synthetic rasters so the script runs anywhere
width = height = 200
transform = from_origin(30.0, 4.0, 0.001, 0.001)  # fake georeference

rng = np.random.default_rng(7)
slope_deg = np.abs(rng.normal(5, 3, (height, width)))          # degrees
dist_to_river_m = np.abs(rng.normal(500, 200, (height, width)))# metres
landcover_green = rng.uniform(0,1,(height, width))              # 0 (impervious) → 1 (forest)
rainfall_index = np.clip(rng.normal(0.5, 0.2, (height, width)), 0, 1)

# 2) Normalise inputs to 0..1 where higher = more susceptible
slope_n = 1 - np.clip(slope_deg/30, 0, 1)       # flatter areas → higher risk
distance_n = 1 - np.clip(dist_to_river_m/1000, 0, 1)  # closer to rivers → higher risk
landcover_n = 1 - landcover_green               # impervious (built‑up) → higher risk
rainfall_n = rainfall_index                     # already 0..1

# 3) Weight the criteria (tweak to taste)
weights = dict(slope=0.25, distance=0.35, landcover=0.2, rainfall=0.2)

susceptibility = (
    weights["slope"] * slope_n +
    weights["distance"] * distance_n +
    weights["landcover"] * landcover_n +
    weights["rainfall"] * rainfall_n
).astype("float32")  # final 0..~1 index

# 4) Save GeoTIFF
meta = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": "float32",
    "crs": "EPSG:4326",
    "transform": transform,
}

with rasterio.open("susceptibility.tif", "w", **meta) as dst:
    dst.write(susceptibility, 1)

print("Wrote susceptibility.tif (open in QGIS to view)." )
