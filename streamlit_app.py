import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# App config
# ==================================================
st.set_page_config(
    page_title="Sandy’s Law — Square, Collapse & Dwell",
    layout="wide"
)

st.title("Sandy’s Law — Bounded Phase-Space & Corner Dwell")
st.caption("Trap → Transition → Escape | Deterministic diagnostic & predictive toy")

# ==================================================
# Utilities
# ==================================================

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def plot_phase(Z, S, title):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, linewidth=1.2)
    ax.set_xlabel("Z (Trap Strength)")
    ax.set_ylabel("Σ (Entropy Escape)")
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_title("Time Series")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def compute_corner_dwell(Z, S, dt, corner_th):
    dwell_steps = 0
    for z, s in zip(Z, S):
        if (z > corner_th and s > corner_th) or \
           (z < 1 - corner_th and s < 1 - corner_th):
            dwell_steps += 1

    dwell_time = dwell_steps * dt
    total_time = len(Z) * dt
    dwell_fraction = dwell_time / total_time if total_time > 0 else 0.0

    return dwell_time, dwell_fraction

# ==================================================
# Toy implementations
# ==================================================

def square_toy(steps, dt):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    for _ in range(steps):
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)
        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)
        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

def coupled_toy(steps, dt, k_zs, k_sz):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    for _ in range(steps):
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)

        dZ += k_zs * (S - 0.5)
        dS += k_sz * (Z - 0.5)

        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

def corner_collapse_toy(
    steps, dt, drive_Z, drive_S, k_collapse, corner_th
):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    def in_corner(z, s):
        return (z > corner_th and s > corner_th) or \
               (z < 1 - corner_th and s < 1 - corner_th)

    for _ in range(steps):
        dZ = drive_Z * np.sign(0.5 - Z)
        dS = drive_S * np.sign(S - 0.5)

        if in_corner(Z, S):
            dZ -= k_collapse * (Z - 0.5)
            dS += k_collapse * (0.5 - S)

        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ==================================================
# Sidebar controls
# ==================================================

st.sidebar.header("Simulation Controls")

mode = st.sidebar.radio(
    "Select Toy",
    [
        "Square (BPSR)",
        "Coupled (Square Breaks)",
        "Square → Corner Collapse"
    ]
)

steps = st.sidebar.slider("Steps", 500, 8000, 4000, 500)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.02, 0.001)
show_timeseries = st.sidebar.checkbox("Show Time Series", value=True)

# Coupling parameters
k_zs = st.sidebar.slider("k_ZΣ (Σ → Z)", -3.0, 3.0, 1.2, 0.1)
k_sz = st.sidebar.slider("k_ΣZ (Z → Σ)", -3.0, 3.0, -0.8, 0.1)

# Collapse parameters
drive_Z = st.sidebar.slider("Drive Z", 0.1, 2.0, 0.6, 0.1)
drive_S = st.sidebar.slider("Drive Σ", 0.1, 2.0, 0.4, 0.1)
k_collapse = st.sidebar.slider("Collapse Strength", 0.5, 5.0, 2.5, 0.1)
corner_th = st.sidebar.slider("Corner Threshold", 0.7, 0.98, 0.9, 0.01)

# ==================================================
# Run selected toy
# ==================================================

if mode == "Square (BPSR)":
    st.subheader("Toy 1 — Bounded Phase-Space Regime (Square)")
    Z, S = square_toy(steps, dt)
    plot_phase(Z, S, "Square: Independent + Clamped")
    if show_timeseries:
        plot_timeseries(Z, S)

elif mode == "Coupled (Square Breaks)":
    st.subheader("Toy 2 — Coupled System (Square Shears)")
    Z, S = coupled_toy(steps, dt, k_zs, k_sz)
    plot_phase(Z, S, "Coupled: Geometry Tilts / Breaks")
    if show_timeseries:
        plot_timeseries(Z, S)

elif mode == "Square → Corner Collapse":
    st.subheader("Toy 3 — Edge Lock → Corner Collapse")
    Z, S = corner_collapse_toy(
        steps, dt, drive_Z, drive_S, k_collapse, corner_th
    )
    plot_phase(Z, S, "Square → Edge Lock → Corner Collapse")

    if show_timeseries:
        plot_timeseries(Z, S)

    # ------------------------------
    # Corner dwell diagnostics (A)
    # ------------------------------
    dwell_time, dwell_fraction = compute_corner_dwell(Z, S, dt, corner_th)

    st.markdown("### 🔴 Corner Dwell Diagnostics")

    col1, col2 = st.columns(2)
    col1.metric("Corner dwell time", f"{dwell_time:.3f} time-units")
    col2.metric("Corner dwell fraction", f"{100*dwell_fraction:.2f} %")

    if dwell_fraction < 0.05:
        st.success("Low corner dwell → Stable / persistent regime")
    elif dwell_fraction < 0.15:
        st.warning("Moderate corner dwell → Pre-instability regime")
    else:
        st.error("High corner dwell → Imminent release likely")

# ==================================================
# Interpretation panel
# ==================================================

with st.expander("Physical Interpretation (Sandy’s Law)", expanded=False):
    st.markdown(
        """
**Square (BPSR)**  
Independent, bounded evolution → time is locked → persistence.

**Coupled regime**  
Σ influences Z and vice versa → geometry tilts → escape possible.

**Corner dwell**  
Time spent in extreme Z–Σ states quantifies instability pressure.

**Key result**  
Corners are not limits — they are failure precursors.
"""
    )