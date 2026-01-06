import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Toy 1 — Square Traversal", layout="wide")
st.title("Toy 1 — Square via Reflecting Boundaries")
st.caption("Independent clocks → bounded square traversal (baseline trapped regime).")

# -------------------------
# Helpers
# -------------------------
def reflect01(x: float, lo: float, hi: float) -> float:
    """Reflect x into [lo, hi] (like a billiard wall)."""
    if lo >= hi:
        return lo
    span = hi - lo
    # bring into [0, 2*span)
    y = (x - lo) % (2 * span)
    # reflect second half
    if y > span:
        y = 2 * span - y
    return lo + y

def plot_phase(Z, S, title, lo, hi):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(Z, S, linewidth=1.0)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title(title)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.grid(True, alpha=0.35)
    ax.set_aspect("equal", adjustable="box")
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("step")
    ax.set_ylabel("value")
    ax.set_title("Time Series (Independent Clocks)")
    ax.legend()
    ax.grid(True, alpha=0.35)
    st.pyplot(fig)
    plt.close(fig)

# -------------------------
# Model (Toy 1)
# -------------------------
def toy1_square(steps: int, dt: float, omega_z: float, omega_s: float, scan_max: float):
    """
    Independent oscillators with reflecting boundaries in [0, scan_max].
    This will fill the square over time if frequencies are incommensurate-ish.
    """
    lo, hi = 0.0, float(scan_max)

    # start away from edges
    Z = 0.62 * hi
    S = 0.41 * hi

    Z_hist = np.empty(steps)
    S_hist = np.empty(steps)

    # simple independent "clock velocities"
    vZ = omega_z * hi
    vS = omega_s * hi

    for i in range(steps):
        Z = reflect01(Z + dt * vZ, lo, hi)
        S = reflect01(S + dt * vS, lo, hi)
        Z_hist[i] = Z
        S_hist[i] = S

    return Z_hist, S_hist, lo, hi

# -------------------------
# UI
# -------------------------
with st.sidebar:
    st.header("Controls")
    steps = st.slider("Steps", 500, 30000, 15000, 500)
    dt = st.slider("dt", 0.001, 0.05, 0.01, 0.001)
    scan_max = st.slider("SCAN MAX (range upper bound)", 1.0, 2.5, 1.68, 0.01)
    omega_z = st.slider("Z clock rate", 0.10, 3.00, 1.00, 0.01)
    omega_s = st.slider("Σ clock rate", 0.10, 3.00, 1.31, 0.01)
    show_ts = st.checkbox("Show time series", True)

Z, S, lo, hi = toy1_square(steps, dt, omega_z, omega_s, scan_max)

plot_phase(Z, S, "Phase Space: Square Traversal", lo, hi)
if show_ts:
    plot_timeseries(Z, S)

st.markdown(
    """
**Interpretation**
- This is your **baseline trapped regime**: Z and Σ evolve independently and remain bounded.
- Over time it explores the available phase space (the square).
- Nothing “collapses” here by design — it’s the reference you compare Toy 2 and Toy 3 against.
"""
)