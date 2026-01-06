import streamlit as st
import numpy as np
from utils.shared_plotting import plot_phase, plot_timeseries, clamp

st.title("Toy 3 — Corner Dwell → Quench")
st.caption("Controlled collapse: square drift + corner-triggered quench dynamics.")

steps = st.sidebar.slider("Steps", 1000, 10000, 5000, 500)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)
drive = st.sidebar.slider("Drive amplitude", 0.1, 2.0, 1.0, 0.05)
quench_strength = st.sidebar.slider("Quench strength", 0.0, 5.0, 2.0, 0.1)
corner_th = st.sidebar.slider("Corner threshold", 0.8, 0.98, 0.9, 0.01)

Z, S = 0.4, 0.6
Zh, Sh = [], []

def in_corner(z, s):
    return (z > corner_th and s > corner_th) or (z < 1 - corner_th and s < 1 - corner_th)

for _ in range(steps):
    dZ = drive * (0.5 - Z)
    dS = drive * (S - 0.5)
    if in_corner(Z, S):
        dZ -= quench_strength * (Z - 0.5)
        dS -= quench_strength * (S - 0.5)
    Z = clamp(Z + dZ * dt)
    S = clamp(S + dS * dt)
    Zh.append(Z)
    Sh.append(S)

Zh, Sh = np.array(Zh), np.array(Sh)

plot_phase(Zh, Sh, "Phase Space: Square → Corner Dwell → Quench")
plot_timeseries(Zh, Sh, "Time Series (Corner Collapse Dynamics)")

corner_dwell = np.mean([in_corner(z, s) for z, s in zip(Zh, Sh)]) * 100
st.metric("Corner Dwell Fraction", f"{corner_dwell:.2f}%")

with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown("""
- Introduces **dwell detection** and **quench response** near corners.  
- Models the **trap → transition → escape** dynamic under stress.  
- Collapse strength controls how sharply the system releases energy.  
- Stable if dwell < 5%, pre-instability if 5–15%, imminent collapse > 15%.
""")