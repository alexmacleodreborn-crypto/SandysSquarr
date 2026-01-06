import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# App config
# ==================================================
st.set_page_config(
    page_title="Sandy’s Law — Square, Coupling & Collapse (Full Fix)",
    layout="wide"
)

st.title("Sandy’s Law — Bounded Phase Space & Corner Collapse")
st.caption("Trap → Transition → Escape | Deterministic diagnostic model")

# ==================================================
# Utilities
# ==================================================

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def plot_phase(Z, S, title):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, linewidth=1.3)
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
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series")
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
    dwell_fraction = dwell_time / (len(Z) * dt)
    return dwell_time, dwell_fraction

# ==================================================
# Core dynamics
# ==================================================

# ---------- TOY 1: TRUE SQUARE (BOUNDARY SEEKING)
def square_toy(steps, dt):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    for _ in range(steps):
        dZ = (Z - 0.5)
        dS = (S - 0.5)

        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ---------- TOY 2: COUPLED (ROTATION + RELAXATION)
def coupled_toy(steps, dt, k_zs, k_sz):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    for _ in range(steps):
        dZ = (0.5 - Z)
        dS = (0.5 - S)

        dZ += k_zs * (S - 0.5)
        dS += k_sz * (Z - 0.5)

        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ---------- TOY 3: SQUARE → CORNER → DWELL → COLLAPSE
def corner_collapse_toy(
    steps, dt, drive_Z, drive_S, k_collapse, corner_th
):
    Z, S = 0.6, 0.4
    Zh, Sh = [], []

    def in_corner(z, s):
        return (z > corner_th and s > corner_th) or \
               (z < 1 - corner_th and s < 1 - corner_th)

    for _ in range(steps):
        # Outward square driver
        dZ = drive_Z * (Z - 0.5)
        dS = drive_S * (S - 0.5)

        # COLLAPSE: quench motion, do not reverse it
        if in_corner(Z, S):
            dZ *= (1 - k_collapse)
            dS *= (1 - k_collapse)

        Z = clamp(Z + dt * dZ, 0, 1)
        S = clamp(S + dt * dS, 0, 1)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ==================================================
# Sidebar
# ==================================================

st.sidebar.header("Controls")

mode = st.sidebar.radio(
    "Toy Mode",
    [
        "Square (BPSR)",
        "Coupled (Shear / Loops)",
        "Square → Corner Collapse"
    ]
)

steps = st.sidebar.slider("Steps", 1000, 9000, 6000, 500)
dt = st.sidebar.slider("dt", 0.005, 0.06, 0.04, 0.001)
show_ts = st.sidebar.checkbox("Show Time Series", True)

k_zs = st.sidebar.slider("k_ZΣ (Σ → Z)", -3.0, 3.0, 1.5, 0.1)
k_sz = st.sidebar.slider("k_ΣZ (Z → Σ)", -3.0, 3.0, -1.2, 0.1)

drive_Z = st.sidebar.slider("Drive Z", 0.5, 2.0, 1.2, 0.1)
drive_S = st.sidebar.slider("Drive Σ", 0.5, 2.0, 1.2, 0.1)
k_collapse = st.sidebar.slider("Collapse Strength", 0.05, 0.9, 0.4, 0.05)
corner_th = st.sidebar.slider("Corner Threshold", 0.75, 0.95, 0.85, 0.01)

# ==================================================
# Run
# ==================================================

if mode == "Square (BPSR)":
    st.subheader("Toy 1 — Bounded Phase-Space Regime (Square)")
    Z, S = square_toy(steps, dt)
    plot_phase(Z, S, "Square: Boundary-Hugging BPSR")
    if show_ts:
        plot_timeseries(Z, S)

elif mode == "Coupled (Shear / Loops)":
    st.subheader("Toy 2 — Coupled System (Shear / Loops)")
    Z, S = coupled_toy(steps, dt, k_zs, k_sz)
    plot_phase(Z, S, "Coupled: Geometry Tilts / Loops")
    if show_ts:
        plot_timeseries(Z, S)

elif mode == "Square → Corner Collapse":
    st.subheader("Toy 3 — Square → Corner → Dwell → Collapse")
    Z, S = corner_collapse_toy(
        steps, dt, drive_Z, drive_S, k_collapse, corner_th
    )
    plot_phase(Z, S, "Square → Corner Collapse")
    if show_ts:
        plot_timeseries(Z, S)

    dwell_t, dwell_f = compute_corner_dwell(Z, S, dt, corner_th)

    st.markdown("### 🔴 Corner Dwell Diagnostics")
    c1, c2 = st.columns(2)
    c1.metric("Corner dwell time", f"{dwell_t:.3f}")
    c2.metric("Corner dwell fraction", f"{100*dwell_f:.2f}%")

    if dwell_f < 0.05:
        st.success("Stable / Persistent")
    elif dwell_f < 0.15:
        st.warning("Pre-instability")
    else:
        st.error("Imminent collapse")

# ==================================================
# Interpretation
# ==================================================

with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown(
        """
• **Square (BPSR)** → bounded phase space, time locked  
• **Coupling** → geometry tilts, time unlocks  
• **Corners** → instability precursors  
• **Collapse strength** → quenching of structure, not reversal  

Corner dwell is the predictive signal.
"""
    )