"""
Flood Detection from Satellite — NDWI (Humanised)
-------------------------------------------------
This script shows the idea behind NDWI (Normalized Difference Water Index).
Replace the synthetic 'green' and 'nir' arrays with actual Sentinel‑2 bands
(resampled and aligned) to detect water/floods.
"""
import numpy as np
import matplotlib.pyplot as plt

def compute_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """NDWI = (Green - NIR) / (Green + NIR)."""
    g = green.astype("float32"); n = nir.astype("float32")
    return (g - n) / (g + n + 1e-6)

def demo_arrays(size: int = 256, seed: int = 3):
    """Create synthetic bands with a rectangular 'water' patch."""
    rng = np.random.default_rng(seed)
    green = rng.integers(500, 3000, (size, size)).astype("uint16")
    nir = rng.integers(500, 3000, (size, size)).astype("uint16")
    # Carve a bright-green / dark-NIR patch to mimic water
    green[80:180, 60:200] = 3200
    nir[80:180, 60:200] = 400
    return green, nir

if __name__ == "__main__":
    green, nir = demo_arrays()
    ndwi = compute_ndwi(green, nir)

    # Very simple threshold for demo purposes
    water_mask = (ndwi > 0.25).astype("uint8")  # 1 = water, 0 = land

    plt.figure(); plt.imshow(ndwi, origin="lower"); plt.title("NDWI"); plt.colorbar()
    plt.figure(); plt.imshow(water_mask, origin="lower"); plt.title("Water Mask (NDWI > 0.25)")
    plt.tight_layout()
    plt.show()
