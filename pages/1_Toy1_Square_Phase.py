import streamlit as st
import numpy as np
from utils.shared_plotting import plot_phase, plot_timeseries

st.title("Toy 1 — Square Phase Traversal")
st.caption("Independent oscillators with reflecting boundaries (bounded phase-space regime).")

steps = st.sidebar.slider("Steps", 500, 25000, 8000, 500)
freq_Z = st.sidebar.slider("Z frequency", 0.9, 2.5, 1.00, 0.01)
freq_S = st.sidebar.slider("Σ frequency", 0.9, 2.5, 1.68, 0.01)

t = np.linspace(0, 2*np.pi*freq_Z, steps)
Z = 0.5 + 0.5 * np.sin(freq_Z * t)
S = 0.5 + 0.5 * np.abs(np.sin(freq_S * t))  # independent oscillation

plot_phase(Z, S, "Phase Space: Square Traversal")
plot_timeseries(Z, S, "Time Series (Independent Clocks)")

with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown("""
- **Z (trap strength)** and **Σ (entropy escape)** oscillate independently.  
- Produces a **square lattice traversal** in phase space.  
- Represents a fully **bounded regime** (no coupling, no instability).
""")