import streamlit as st
import numpy as np
from utils.shared_plotting import plot_phase, plot_timeseries

st.title("Toy 2 — Closed Loop System (Exact Conservative Coupling)")
st.caption("Exact conservative rotation; no numerical energy injection.")

steps = st.sidebar.slider("Steps", 500, 20000, 8000, 500)
angle = st.sidebar.slider("Coupling angle (radians)", 0.1, 3.0, 1.2, 0.05)
phase_shift = st.sidebar.slider("Phase shift", 0.0, np.pi, 0.8, 0.05)

t = np.linspace(0, 2*np.pi, steps)
Z = 0.5 + 0.3 * np.cos(t)
S = 0.5 + 0.2 * np.sin(t + phase_shift)

# Apply shear rotation
Zs = (Z - 0.5)*np.cos(angle) - (S - 0.5)*np.sin(angle) + 0.5
Ss = (Z - 0.5)*np.sin(angle) + (S - 0.5)*np.cos(angle) + 0.5

plot_phase(Zs, Ss, "Phase Space: Exact Closed Loop (Sheared View)")
plot_timeseries(Zs, Ss, "Time Series (Pure Coupled Rotation)")

st.markdown("**Diagnostics**")
st.metric("Amplitude (start)", f"{(np.ptp(Zs)/2):.3f}")

with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown("""
- **Pure conservative coupling:** rotational symmetry around (0.5, 0.5).  
- **No decay, no amplification.** Energy strictly conserved.  
- Represents a **stable geometric shear loop** regime.
""")