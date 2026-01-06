"""
Sandy's Law — Square / Coupling / Corner Collapse Toys
=====================================================

This file reproduces all toy behaviours discussed in the chat:

1. Square (Bounded Phase-Space Regime, BPSR)
2. Coupled system (square shears / breaks)
3. Square → Edge Lock → Corner Collapse
4. Time series diagnostics

Author: Sandy's Law Project
"""

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# Utilities
# --------------------------------------------------

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def plot_phase(Z, S, title):
    plt.figure(figsize=(5, 5))
    plt.plot(Z, S, linewidth=1.2)
    plt.xlabel("Z (Trap Strength)")
    plt.ylabel("Σ (Entropy Escape)")
    plt.title(title)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.gca().set_aspect('equal')
    plt.grid(True, alpha=0.4)
    plt.show()

# --------------------------------------------------
# TOY 1: Square (Independent + Clamped)
# --------------------------------------------------

def run_square_toy(steps=4000, dt=0.02):
    Z, S = 0.6, 0.4
    Z_hist, S_hist = [], []

    for t in range(steps):
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)

        Z = clamp(Z + dt * dZ, 0.0, 1.0)
        S = clamp(S + dt * dS, 0.0, 1.0)

        Z_hist.append(Z)
        S_hist.append(S)

    return np.array(Z_hist), np.array(S_hist)

# --------------------------------------------------
# TOY 2: Coupled (Square Breaks / Shears)
# --------------------------------------------------

def run_coupled_toy(steps=4000, dt=0.02, k_zs=1.2, k_sz=-0.8):
    Z, S = 0.6, 0.4
    Z_hist, S_hist = [], []

    for t in range(steps):
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)

        # Coupling terms
        dZ += k_zs * (S - 0.5)
        dS += k_sz * (Z - 0.5)

        Z = clamp(Z + dt * dZ, 0.0, 1.0)
        S = clamp(S + dt * dS, 0.0, 1.0)

        Z_hist.append(Z)
        S_hist.append(S)

    return np.array(Z_hist), np.array(S_hist)

# --------------------------------------------------
# TOY 3: Square → Edge Lock → Corner Collapse
# --------------------------------------------------

def run_corner_collapse_toy(
    steps=5000,
    dt=0.01,
    drive_Z=0.6,
    drive_S=0.4,
    k_collapse=2.5,
    corner_threshold=0.9
):
    Z, S = 0.6, 0.4
    Z_hist, S_hist = [], []

    def in_corner(z, s):
        return (z > corner_threshold and s > corner_threshold) or \
               (z < 1 - corner_threshold and s < 1 - corner_threshold)

    for t in range(steps):

        # Independent drives (square-forming)
        dZ = drive_Z * np.sign(0.5 - Z)
        dS = drive_S * np.sign(S - 0.5)

        # Corner-triggered collapse
        if in_corner(Z, S):
            dZ -= k_collapse * (Z - 0.5)
            dS += k_collapse * (0.5 - S)

        Z = clamp(Z + dt * dZ, 0.0, 1.0)
        S = clamp(S + dt * dS, 0.0, 1.0)

        Z_hist.append(Z)
        S_hist.append(S)

    return np.array(Z_hist), np.array(S_hist)

# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    # --- Toy 1: Square ---
    Z1, S1 = run_square_toy()
    plot_phase(Z1, S1, "Toy 1: Square (Bounded Phase-Space Regime)")

    # --- Toy 2: Coupled ---
    Z2, S2 = run_coupled_toy()
    plot_phase(Z2, S2, "Toy 2: Coupled (Square Breaks / Shears)")

    # --- Toy 3: Corner Collapse ---
    Z3, S3 = run_corner_collapse_toy()
    plot_phase(Z3, S3, "Toy 3: Square → Edge Lock → Corner Collapse")

    # --- Time series (square mode) ---
    plt.figure(figsize=(7, 3))
    plt.plot(Z1, label="Z (square mode)")
    plt.plot(S1, label="Σ (square mode)")
    plt.title("Time Series — Square Mode")
    plt.xlabel("step")
    plt.ylabel("value")
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.show()