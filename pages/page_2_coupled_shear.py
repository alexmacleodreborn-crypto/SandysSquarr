import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="Toy 2 — Coupled Shear Loops (Fixed)",
    layout="wide"
)

st.title("Toy 2 — Coupled System (Stable Sheared Loops) — FIXED")
st.caption("Pure skew coupling → closed loops (area-preserving). Shear is geometric ONLY (plot transform).")

# ==================================================
# Sidebar controls
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider("Steps", 1000, 50000, 20000, 1000)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)

omega = st.sidebar.slider("Coupling ω (loop speed)", 0.1, 20.0, 4.0, 0.1)
kickZ = st.sidebar.slider("Initial kick Z", -0.45, 0.45, 0.18, 0.01)
kickS = st.sidebar.slider("Initial kick Σ", -0.45, 0.45, 0.00, 0.01)

# Shear is applied ONLY for plotting (coordinate transform)
shear = st.sidebar.slider("Shear (plot-only tilt)", -3.0, 3.0, 1.0, 0.1)

plot_stride = st.sidebar.slider(
    "Plot stride (rendering performance)",
    1, 50, 1, 1
)
show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Core dynamics — pure skew-symmetric rotation about (0.5, 0.5)
#   dZ =  ω * (Σ - 0.5)
#   dΣ = -ω * (Z - 0.5)
# This is conservative: it produces CLOSED LOOPS with no decay.
# ==================================================
Z = 0.5 + kickZ
S = 0.5 + kickS

Zh, Sh = [], []

for _ in range(steps):
    zc = Z - 0.5
    sc = S - 0.5

    dZ = omega * sc
    dS = -omega * zc

    Z = Z + dt * dZ
    S = S + dt * dS

    Zh.append(Z)
    Sh.append(S)

Z_arr = np.array(Zh)
S_arr = np.array(Sh)

# ==================================================
# Plot transform (geometric shear ONLY)
#   We shear the coordinates for display, then normalize back to [0,1]
#   so the axes remain comparable to other toys.
# ==================================================
zc = Z_arr - 0.5
sc = S_arr - 0.5

# Apply shear to centered coordinates
zc_plot = zc + shear * sc
sc_plot = sc

Z_plot = zc_plot + 0.5
S_plot = sc_plot + 0.5

# Keep the plot view in [0,1] by clipping ONLY for drawing (not dynamics)
Zp = np.clip(Z_plot, 0.0, 1.0)[::plot_stride]
Sp = np.clip(S_plot, 0.0, 1.0)[::plot_stride]

# Downsample original time series for display
Zt = Z_arr[::plot_stride]
St = S_arr[::plot_stride]

# ==================================================
# Plot helpers
# ==================================================
def plot_phase(Z, S):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, lw=1.2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title("Phase Space: Closed Loop (Sheared View)")
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series (Pure Coupled Rotation)")
    ax.legend()
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# Display
# ==================================================
st.subheader("Phase Space")
plot_phase(Zp, Sp)

if show_ts:
    st.subheader("Time Series")
    plot_timeseries(Zt, St)

# ==================================================
# Diagnostics: amplitude should NOT decay
# ==================================================
amp = np.sqrt((Z_arr - 0.5) ** 2 + (S_arr - 0.5) ** 2)
amp0 = float(amp[0])
amp_end = float(amp[-1])

st.markdown("### Diagnostics")
c1, c2 = st.columns(2)
c1.metric("Initial amplitude", f"{amp0:.4f}")
c2.metric("Final amplitude", f"{amp_end:.4f}")

if abs(amp_end - amp0) / (amp0 + 1e-12) < 0.02:
    st.success("Conservative loops confirmed (no decay).")
else:
    st.warning("Amplitude drift detected (try smaller dt).")

# ==================================================
# Interpretation
# ==================================================
with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown(
        """
**What this toy demonstrates**

• Z and Σ are **coupled** in a conservative way  
• The trajectory forms **closed loops** (no spirals inward)  
• This represents a “time-unlocked” oscillatory regime  
• **Shear** here is purely geometric: it tilts the loop but does not change dynamics  

**Controls**

• ω: loop speed  
• kickZ/kickΣ: loop radius + orientation  
• shear: visual tilt (plot transform only)  

If you see decay → reduce dt.
"""
    )