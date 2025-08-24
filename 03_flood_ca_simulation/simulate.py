"""
Flood Spread Simulation (Humanised)
-----------------------------------
A tiny cellular-automata style model to see how water might accumulate and
spread across a simple landscape (a synthetic DEM). This is for learning
the *idea*, not for engineering decisions.
"""

import numpy as np
import matplotlib.pyplot as plt

def make_synthetic_dem(size: int = 120, seed: int = 1) -> np.ndarray:
    """Create a bumpy downhill surface (metres)."""
    rng = np.random.default_rng(seed)
    base_slope = np.linspace(3, 0, size)[:, None]  # downhill from top to bottom
    waves = 0.3 * np.sin(np.linspace(0, 6*np.pi, size))[None, :]
    rough = 0.2 * rng.normal(size=(size, size))
    return base_slope + waves + rough

def simulate(dem: np.ndarray, rainfall_mm: float = 120, steps: int = 250,
             infiltration_m: float = 0.002, allow_edge_outflow: bool = True) -> np.ndarray:
    """
    Run a simple water accumulation simulation.

    Args:
        dem: 2D array of elevations (m).
        rainfall_mm: total rainfall added over all steps (mm).
        steps: number of timesteps.
        infiltration_m: water lost per cell per step (m).
        allow_edge_outflow: if True, some water exits at the borders.

    Returns:
        water: 2D array of water depth at the end (m).
    """
    water = np.zeros_like(dem)
    rain_per_step = (rainfall_mm / 1000.0) / steps  # m per step

    # Von Neumann neighbourhood (N,S,E,W)
    neighbours = [(-1,0),(1,0),(0,-1),(0,1)]

    for _ in range(steps):
        # 1) Add rainfall
        water += rain_per_step

        # 2) Compute water surface (elevation + water)
        H = dem + water

        # 3) Push water from higher cells to lower neighbours (very simplified)
        flux = np.zeros_like(H)
        for di, dj in neighbours:
            shifted = np.roll(np.roll(H, di, axis=0), dj, axis=1)
            dH = H - shifted
            flux += np.clip(dH, 0, None)

        moved = 0.2 * flux  # how much water to move this step
        water = np.clip(water - moved, 0, None)

        for di, dj in neighbours:
            water += 0.05 * np.roll(np.roll(moved, -di, axis=0), -dj, axis=1)

        # 4) Infiltration (loss to soil)
        water = np.clip(water - infiltration_m, 0, None)

        # 5) Let some water leave at the boundary
        if allow_edge_outflow:
            water[0,:] *= 0.7; water[-1,:] *= 0.7; water[:,0] *= 0.7; water[:,-1] *= 0.7

    return water

if __name__ == "__main__":
    dem = make_synthetic_dem()
    water = simulate(dem, rainfall_mm=120, steps=250)

    plt.figure(figsize=(6,5))
    plt.imshow(water, origin="lower")
    plt.title("Simulated Flood Water Depth (m)")
    plt.colorbar(label="m")
    plt.tight_layout()
    plt.show()
