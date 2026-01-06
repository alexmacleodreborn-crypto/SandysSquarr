import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import lightkurve as lk

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Toy 3 — Corner Dwell & Quench (LightCurve)",
    layout="wide"
)

st.title("Toy 3 — Corner Dwell & Quench")
st.caption("Escape-controlled evolution using real LightCurve data")

# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("Data Source")

target = st.sidebar.text_input(
    "TESS Target (validation star)",
    value="TIC 141914082"
)

z_th = st.sidebar.slider("Z threshold (trap)", 0.5, 0.95, 0.7, 0.01)
s_th = st.sidebar.slider("Σ threshold (escape)", 0.05, 0.5, 0.25, 0.01)

smooth_order = st.sidebar.slider("Smoothing order", 2, 5, 3)
max_window = st.sidebar.slider("Max smoothing window", 9, 51, 31, 2)

# ============================================================
# LOAD LIGHT CURVE (SAFE)
# ============================================================

@st.cache_data(show_spinner=False)
def load_lightcurve(target):
    search = lk.search_lightcurve(target, mission="TESS")
    if len(search) == 0:
        return None
    lc = search.download()
    return lc.remove_nans()

lc = load_lightcurve(target)

if lc is None:
    st.error("No TESS light curve found for this target.")
    st.stop()

time = lc.time.value
flux = lc.flux.value

st.success(f"Loaded {len(time)} data points")

# ============================================================
# NORMALIZE & SMOOTH
# ============================================================

flux = flux / np.nanmedian(flux)

N = len(flux)
window = min(max_window, (N // 2) * 2 - 1)

if window < 5:
    st.error("Not enough data points to smooth safely.")
    st.stop()

flux_smooth = savgol_filter(flux, window, smooth_order)

# ============================================================
# TOY 3 VARIABLES
# ============================================================

Sigma = (flux_smooth - flux_smooth.min()) / (
    flux_smooth.max() - flux_smooth.min()
)

dt = np.gradient(time)
dSigma_dt = np.gradient(Sigma) / dt
d2Sigma_dt2 = np.gradient(dSigma_dt) / dt

A = np.nanmax(np.abs(dSigma_dt))
Z = 1.0 - np.abs(dSigma_dt) / A
Z = np.clip(Z, 0, 1)

# ============================================================
# CORNER & QUENCH
# ============================================================

corner_mask = (Z > z_th) & (Sigma < s_th)

corner_time = np.sum(corner_mask) * np.nanmedian(dt)
corner_fraction = np.sum(corner_mask) / len(Z)

quench_index = np.argmax(np.abs(d2Sigma_dt2))
quench_time = time[quench_index]

# ============================================================
# METRICS
# ============================================================

st.subheader("Toy 3 Diagnostics")

c1, c2, c3 = st.columns(3)
c1.metric("Corner dwell time (days)", f"{corner_time:.4f}")
c2.metric("Corner dwell fraction", f"{corner_fraction*100:.2f}%")
c3.metric("Quench time (BTJD)", f"{quench_time:.4f}")

# ============================================================
# PLOTS
# ============================================================

st.subheader("Diagnostics")

col1, col2, col3 = st.columns(3)

with col1:
    fig, ax = plt.subplots(figsize=(5,5))
    ax.plot(Z, Sigma, lw=1.4)
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_xlabel("Z (Trap proxy)")
    ax.set_ylabel("Σ (Escape proxy)")
    ax.set_title("Phase Space")
    ax.grid(alpha=0.4)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(time, Sigma, label="Σ", lw=1.4)
    ax.plot(time, Z, label="Z", lw=1.2)
    ax.axvline(quench_time, color="r", ls="--", label="Quench")
    ax.set_xlabel("Time (BTJD)")
    ax.set_title("Time Series")
    ax.legend()
    ax.grid(alpha=0.4)
    st.pyplot(fig)

with col3:
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(time, corner_mask.astype(int), lw=1.5)
    ax.set_xlabel("Time (BTJD)")
    ax.set_ylabel("Corner")
    ax.set_title("Corner Dwell Indicator")
    ax.grid(alpha=0.4)
    st.pyplot(fig)

# ============================================================
# INTERPRETATION
# ============================================================

with st.expander("What this means (Toy 3 interpretation)"):
    st.markdown(
        """
• High **Z** + low **Σ** = trapped state  
• **Corner dwell** = delayed escape  
• **Quench** = release / transition  
• Late smooth behaviour hides early structure  

This diagnostic is **model-independent** and measures
*escape-controlled evolution* directly.
"""
    )