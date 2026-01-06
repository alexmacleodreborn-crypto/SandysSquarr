import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="Toy 3 — Corner Dwell → Quench",
    layout="wide"
)

st.title("Toy 3 — Corner Dwell → Quench (Controlled Collapse)")
st.caption("Base motion: exact conservative loops (Toy 2). New ingredient: corner-triggered quench.")

# ==================================================
# Sidebar controls
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider("Steps", 1000, 80000, 30000, 1000)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)

omega = st.sidebar.slider("ω (loop frequency)", 0.1, 20.0, 4.0, 0.1)

kickZ = st.sidebar.slider("Initial Z offset", -0.45, 0.45, 0.22, 0.01)
kickS = st.sidebar.slider("Initial Σ offset", -0.45, 0.45, 0.10, 0.01)

# Corner / quench parameters
corner_th = st.sidebar.slider("Corner threshold", 0.70, 0.98, 0.85, 0.01)
quench_strength = st.sidebar.slider("Quench strength (0..1)", 0.0, 1.0, 0.25, 0.01)
quench_target = st.sidebar.selectbox(
    "Quench target",
    ["Center (0.5,0.5)", "Low-Low corner", "High-High corner"]
)

# Optional geometry for plotting only
shear = st.sidebar.slider("Shear (plot-only tilt)", -3.0, 3.0, 1.0, 0.1)

stride = st.sidebar.slider("Plot stride", 1, 80, 3, 1)
show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Helpers
# ==================================================
def in_corner(z, s, th):
    # Two "instability" corners:
    # (high, high) and (low, low)
    return (z >= th and s >= th) or (z <= 1 - th and s <= 1 - th)

def corner_name(z, s, th):
    if z >= th and s >= th:
        return "HH"
    if z <= 1 - th and s <= 1 - th:
        return "LL"
    return "None"

def target_point(which, th):
    if which == "Center (0.5,0.5)":
        return 0.5, 0.5
    if which == "Low-Low corner":
        return (1 - th), (1 - th)
    if which == "High-High corner":
        return th, th
    return 0.5, 0.5

# ==================================================
# Core dynamics
# Base step: exact conservative rotation (Toy 2 core)
# Corner step: apply quench (dissipation) ONLY when in corner
# ==================================================
Z = 0.5 + kickZ
S = 0.5 + kickS

Zh, Sh = [], []
corner_hits = 0
corner_steps = 0
corner_run_lengths = []
current_run = 0

theta = omega * dt
c, s = np.cos(theta), np.sin(theta)

tZ, tS = target_point(quench_target, corner_th)

for _ in range(steps):
    # --- Exact conservative step (rotation about center)
    zc = Z - 0.5
    sc = S - 0.5
    zc_new =  c * zc + s * sc
    sc_new = -s * zc + c * sc
    Z = zc_new + 0.5
    S = sc_new + 0.5

    # --- Corner-triggered quench (the ONLY new physics)
    if in_corner(Z, S, corner_th):
        corner_steps += 1
        current_run += 1

        # Quench: pull toward target point (dissipative)
        Z = (1 - quench_strength) * Z + quench_strength * tZ
        S = (1 - quench_strength) * S + quench_strength * tS
    else:
        if current_run > 0:
            corner_run_lengths.append(current_run)
            corner_hits += 1
            current_run = 0

    Zh.append(Z)
    Sh.append(S)

# close final run
if current_run > 0:
    corner_run_lengths.append(current_run)
    corner_hits += 1

Z_arr = np.array(Zh)
S_arr = np.array(Sh)

# ==================================================
# Plot transform (visual shear only)
# ==================================================
zc = Z_arr - 0.5
sc_ = S_arr - 0.5
Zp = np.clip(zc + shear * sc_ + 0.5, 0, 1)[::stride]
Sp = np.clip(sc_ + 0.5, 0, 1)[::stride]

Zt = Z_arr[::stride]
St = S_arr[::stride]

# ==================================================
# Plots
# ==================================================
st.subheader("Phase Space")
fig, ax = plt.subplots(figsize=(5, 5))
ax.plot(Zp, Sp, lw=1.1)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("equal")
ax.set_xlabel("Z (trap strength)")
ax.set_ylabel("Σ (entropy escape)")
ax.set_title("Square → Corner Dwell → Quench")
ax.grid(True, alpha=0.4)

# draw corner boxes for clarity
th = corner_th
ax.axvline(th, alpha=0.15)
ax.axhline(th, alpha=0.15)
ax.axvline(1 - th, alpha=0.15)
ax.axhline(1 - th, alpha=0.15)

st.pyplot(fig)
plt.close(fig)

if show_ts:
    st.subheader("Time Series")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Zt, label="Z")
    ax.plot(St, label="Σ")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series (Exact + Corner Quench)")
    ax.legend()
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# Corner diagnostics
# ==================================================
st.subheader("🔴 Corner Dwell Diagnostics")

dwell_fraction = corner_steps / max(1, steps)
dwell_time = corner_steps * dt
avg_run = float(np.mean(corner_run_lengths)) if corner_run_lengths else 0.0
max_run = int(np.max(corner_run_lengths)) if corner_run_lengths else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Corner dwell fraction", f"{100*dwell_fraction:.2f}%")
c2.metric("Corner dwell time", f"{dwell_time:.3f}")
c3.metric("Corner entries", f"{corner_hits}")
c4.metric("Max corner run (steps)", f"{max_run}")

# Qualitative status
if dwell_fraction < 0.05:
    st.success("Stable / Persistent (rare corner capture)")
elif dwell_fraction < 0.15:
    st.warning("Pre-instability (frequent corner visits)")
else:
    st.error("Instability / Collapse (corner-captured)")

# ==================================================
# Interpretation
# ==================================================
with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown(
        """
**What Toy 3 adds on top of Toy 2**

• Base motion is **exact conservative coupling** (closed loops).  
• Corners represent **instability gates** (trap saturation states).  
• When the system enters a corner, a **quench** is applied (dissipation / collapse mechanism).  
• The diagnostic is the **dwell fraction**: how much time is spent in the instability zone.

**Controls**

• Corner threshold: defines the instability region size  
• Quench strength: how strongly the system is pulled once inside  
• Quench target: where the collapse “lands” (center or specific corner)

This is the minimal deterministic **precursor → dwell → collapse** model.
"""
    )