import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="Toy 1 — Square Phase Space",
    layout="wide"
)

st.title("Toy 1 — Bounded Phase Space (Square)")
st.caption("Independent clocks → bounded square traversal")

# ==================================================
# Controls
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider("Steps", 500, 10000, 5000, 500)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)

Tz = st.sidebar.slider("Z period", 0.5, 5.0, 1.0, 0.1)
Ts = st.sidebar.slider("Σ period", 0.5, 5.0, 1.7, 0.1)

show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Core dynamics — independent clocks
# ==================================================

t = np.arange(steps) * dt

Z = (t / Tz) % 1.0
S = (t / Ts) % 1.0

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
    ax.set_title("Phase Space: Square Traversal")
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series (Independent Clocks)")
    ax.legend()
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# Display
# ==================================================

st.subheader("Phase Space")
plot_phase(Z, S)

if show_ts:
    st.subheader("Time Series")
    plot_timeseries(Z, S)

# ==================================================
# Interpretation
# ==================================================

with st.expander("Physical Interpretation"):
    st.markdown(
        """
**What you are seeing**

• Z and Σ evolve independently  
• Each variable is bounded in [0, 1]  
• The system explores the full square  
• No coupling, no collapse, no damping  

**Why this matters**

This is the **baseline trapped regime** in Sandy’s Law.

Time exists, but:
- it is local
- it is bounded
- it does not unlock escape

Every other toy must be compared **against this reference**.
"""
    )