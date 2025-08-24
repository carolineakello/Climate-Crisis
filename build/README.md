# Flood Data Visualisation Dashboard (Humanised)

**What it does:** Interactive plots of rainfall and discharge, plus a demo map of flood‑prone locations.

## Run
```bash
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:8050
```

## Replace with your data
- Put your CSV with a `date` column into `data/` and update the code to match your columns.
- Replace `data/flood_prone.geojson` with real points or polygons.
