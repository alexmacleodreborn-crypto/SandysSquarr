import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Toy 3 — Corner Collapse", layout="wide")
st.title("Toy 3 — Edge Lock → Corner Collapse")
st.caption("Edge-lock regime with conditional corner collapse + dwell diagnostics.")

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def in_corner(z, s, th):
    return (z > th and s > th) or (z < 1 - th and s < 1 - th)

def simulate_collapse(steps, dt, Z0, S0, drive_Z, drive_S, k_collapse, corner_th):
    Z, S = Z0, S0
    Zh, Sh = [], []
    corner_hits = []

    for _ in range(steps):
        # Your "worked" base dynamics (edge-lock-ish)
        dZ = drive_Z * (0.5 - Z)
        dS = drive_S * (S - 0.5)

        if in_corner(Z, S, corner_th):
            # Your "worked" collapse impulse
            dZ -= k_collapse * (Z - 0.5)
            dS += k_collapse * (0.5 - S)
            corner_hits.append(1)
        else:
            corner_hits.append(0)

        Z = clamp(Z + dt * dZ)
        S = clamp(S + dt * dS)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh), np.array(corner_hits)

def plot_phase(Z, S, hits=None, th=0.85):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.plot(Z, S, lw=1.2)

    # Optional corner markers
    if hits is not None and hits.sum() > 0:
        idx = np.where(hits > 0)[0]
        ax.scatter(Z[idx], S[idx], s=12)

    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.35)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title("Square → Edge Lock → Corner Collapse")
    st.pyplot(fig); plt.close(fig)

def plot_ts(Z, S):
    fig, ax = plt.subplots(figsize=(7,3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.grid(True, alpha=0.35)
    ax.set_xlabel("step"); ax.set_ylabel("value")
    ax.set_title("Time Series")
    ax.legend()
    st.pyplot(fig); plt.close(fig)

def corner_dwell(hits, dt):
    dwell_steps = int(hits.sum())
    dwell_time = dwell_steps * dt
    dwell_frac = dwell_steps / len(hits) if len(hits) else 0.0
    return dwell_time, dwell_frac

with st.sidebar:
    st.header("Toy 3 Controls")
    steps = st.slider("Steps", 500, 12000, 5000, 500)
    dt = st.slider("dt", 0.001, 0.06, 0.03, 0.001)
    Z0 = st.slider("Z0", 0.0, 1.0, 0.60, 0.01)
    S0 = st.slider("Σ0", 0.0, 1.0, 0.40, 0.01)

    drive_Z = st.slider("Drive Z", 0.5, 2.0, 1.0, 0.1)
    drive_S = st.slider("Drive Σ", 0.5, 2.0, 1.2, 0.1)
    k_collapse = st.slider("Collapse Strength", 0.5, 5.0, 2.5, 0.1)
    corner_th = st.slider("Corner Threshold", 0.75, 0.95, 0.85, 0.01)

    show_ts = st.checkbox("Show Time Series", True)
    show_corner_points = st.checkbox("Highlight corner points", True)

Z, S, hits = simulate_collapse(steps, dt, Z0, S0, drive_Z, drive_S, k_collapse, corner_th)

c1, c2 = st.columns([1,1])
with c1:
    plot_phase(Z, S, hits if show_corner_points else None, corner_th)
with c2:
    if show_ts:
        plot_ts(Z, S)

dwell_t, dwell_f = corner_dwell(hits, dt)

st.markdown("### 🔴 Corner Dwell Diagnostics")
m1, m2, m3 = st.columns(3)
m1.metric("Corner hits (steps)", f"{int(hits.sum())}")
m2.metric("Corner dwell time", f"{dwell_t:.3f}")
m3.metric("Corner dwell fraction", f"{100*dwell_f:.2f}%")

if dwell_f == 0:
    st.warning("No corner entry detected. Reduce corner threshold (e.g. 0.85→0.80) and/or increase dt or drives.")
elif dwell_f < 0.05:
    st.success("Stable / Persistent")
elif dwell_f < 0.15:
    st.warning("Pre-instability")
else:
    st.error("Imminent collapse")