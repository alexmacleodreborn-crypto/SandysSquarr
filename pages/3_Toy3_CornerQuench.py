import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Toy 3 — Corner Dwell → Quench", layout="wide")
st.title("Toy 3 — Corner Dwell → Quench (Controlled Collapse)")
st.caption("Base motion: Toy 2 closed loops. New ingredient: corner-triggered quench + dwell diagnostics.")

# -------------------------
# Helpers
# -------------------------
def plot_phase(Z, S, title):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(Z, S, linewidth=1.0)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
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
    ax.set_title("Time Series")
    ax.legend()
    ax.grid(True, alpha=0.35)
    st.pyplot(fig)
    plt.close(fig)

def in_corner(z, s, corner_th):
    # high-high OR low-low
    return (z > corner_th and s > corner_th) or (z < (1 - corner_th) and s < (1 - corner_th))

def corner_dwell_stats(Z, S, corner_th):
    flags = np.array([in_corner(z, s, corner_th) for z, s in zip(Z, S)], dtype=bool)
    dwell_steps = int(flags.sum())
    dwell_frac = float(dwell_steps / len(flags)) if len(flags) else 0.0

    # entries + max run
    entries = 0
    max_run = 0
    run = 0
    prev = False
    for f in flags:
        if f and not prev:
            entries += 1
        if f:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
        prev = f

    return dwell_steps, dwell_frac, entries, max_run

# -------------------------
# Model (Toy 3)
# -------------------------
def toy3_corner_quench(
    steps: int,
    theta: float,
    amp: float,
    shear: float,
    corner_th: float,
    quench_strength: float,
    centre=(0.5, 0.5),
):
    """
    Conservative rotation about centre (Toy 2).
    If the trajectory enters a corner region, apply a quench that shrinks amplitude.
    """
    cx, cy = centre
    u, v = amp, -0.6 * amp

    Z = np.empty(steps)
    S = np.empty(steps)

    c = np.cos(theta)
    s = np.sin(theta)

    for i in range(steps):
        # exact conservative rotation
        u, v = (c * u - s * v), (s * u + c * v)

        # map
        z = cx + u
        sig = cy + v

        # shear view (optional)
        if shear != 0.0:
            dz = z - cx
            ds = sig - cy
            z = cx + dz + shear * ds
            sig = cy + ds

        # corner-triggered quench:
        # shrink the underlying amplitude (u,v), not just (z,s)
        if in_corner(float(np.clip(z, 0, 1)), float(np.clip(sig, 0, 1)), corner_th):
            u *= (1.0 - quench_strength)
            v *= (1.0 - quench_strength)

        z = float(np.clip(cx + u, 0.0, 1.0))
        sig = float(np.clip(cy + v, 0.0, 1.0))

        Z[i] = z
        S[i] = sig

    return Z, S

# -------------------------
# UI
# -------------------------
with st.sidebar:
    st.header("Controls")
    steps = st.slider("Steps", 500, 50000, 15000, 500)
    theta = st.slider("Rotation per step (θ)", 0.001, 0.25, 0.03, 0.001)
    amp = st.slider("Amplitude", 0.01, 0.49, 0.22, 0.01)
    shear = st.slider("Shear (view tilt)", -1.50, 1.50, 0.60, 0.05)
    corner_th = st.slider("Corner threshold", 0.70, 0.95, 0.85, 0.01)
    quench_strength = st.slider("Quench strength", 0.00, 0.20, 0.03, 0.005)
    show_ts = st.checkbox("Show time series", True)

Z, S = toy3_corner_quench(steps, theta, amp, shear, corner_th, quench_strength)

plot_phase(Z, S, "Phase Space: Corner Dwell → Quench")
if show_ts:
    plot_timeseries(Z, S)

dwell_steps, dwell_frac, entries, max_run = corner_dwell_stats(Z, S, corner_th)

st.markdown("## 🔴 Corner Dwell Diagnostics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Corner dwell fraction", f"{100*dwell_frac:.2f}%")
c2.metric("Corner dwell (steps)", f"{dwell_steps}")
c3.metric("Corner entries", f"{entries}")
c4.metric("Max corner run (steps)", f"{max_run}")

if dwell_frac < 0.05:
    st.success("Stable / Persistent (rare corner capture)")
elif dwell_frac < 0.15:
    st.warning("Pre-instability (corner residency rising)")
else:
    st.error("High instability risk (sustained corner capture)")