"""
Flood Loss & Damage Estimation (Humanised)
------------------------------------------
Estimate economic loss for buildings given a flood depth raster
and a depth–damage curve. Uses synthetic data so the script runs
anywhere; replace with real rasters and building footprints.
"""
import json
import numpy as np
import rasterio
from rasterio.transform import from_origin

def write_demo_raster(width=150, height=150):
    """Make a simple 'pond' of flood depth in metres and save as GeoTIFF."""
    transform = from_origin(32.0, 1.0, 0.001, 0.001)
    y, x = np.mgrid[0:height, 0:width]
    depth = 2.0 * np.exp(-((x-75)**2 + (y-70)**2)/(2*30**2))  # gaussian mound
    meta = {"driver":"GTiff","height":height,"width":width,"count":1,
            "dtype":"float32","crs":"EPSG:4326","transform":transform}
    with rasterio.open("flood_depth.tif", "w", **meta) as dst:
        dst.write(depth.astype("float32"), 1)
    return transform

def write_demo_buildings(n=80):
    """Create random building points with property values (USD)."""
    rng = np.random.default_rng(5)
    feats = []
    for i in range(n):
        lon = 32.0 + rng.uniform(0, 0.15)     # match the raster extent
        lat = 1.0 - rng.uniform(0, 0.15)
        value = int(rng.integers(10000, 200000))
        feats.append({
            "type":"Feature",
            "properties":{"id": i, "value_usd": value},
            "geometry":{"type":"Point","coordinates":[float(lon), float(lat)]}
        })
    geojson = {"type":"FeatureCollection","features":feats}
    with open("buildings.geojson","w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    return geojson

def depth_damage_fraction(depth_m: float) -> float:
    """Toy depth–damage curve returning loss fraction 0..1."""
    if depth_m <= 0: return 0.0
    if depth_m < 0.2: return 0.1*depth_m/0.2       # up to 10%
    if depth_m < 1.0: return 0.1 + 0.4*(depth_m-0.2)/0.8  # up to 50%
    if depth_m < 2.0: return 0.5 + 0.4*(depth_m-1.0)/1.0  # up to 90%
    return 0.95

if __name__ == "__main__":
    print("Creating demo raster and buildings...")
    transform = write_demo_raster()
    buildings = write_demo_buildings()

    print("Sampling flood depth at each building and estimating loss...")
    import rasterio.sample as rs
    total_loss = 0.0

    with rasterio.open("flood_depth.tif") as src:
        coords = [tuple(feat["geometry"]["coordinates"]) for feat in buildings["features"]]
        for feat, depth in zip(buildings["features"], src.sample(coords)):
            d = float(depth[0])
            frac = depth_damage_fraction(d)
            loss = frac * feat["properties"]["value_usd"]
            feat["properties"]["depth_m"] = round(d, 3)
            feat["properties"]["loss_usd"] = round(loss, 2)
            total_loss += loss

    with open("losses.geojson","w", encoding="utf-8") as f:
        json.dump(buildings, f, indent=2)

    print(f"Estimated total loss (USD): {round(total_loss,2):,.2f}")
    print("Wrote: flood_depth.tif, buildings.geojson, losses.geojson")
