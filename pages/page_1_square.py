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
st.caption("Independent clocks → deterministic square traversal")

# ==================================================
# Sidebar controls
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider(
    "Steps (simulation length)",
    1000, 50000, 20000, 1000
)

dt = st.sidebar.slider(
    "dt (time step)",
    0.001, 0.05, 0.013, 0.001
)

Tz = st.sidebar.slider(
    "Z period",
    0.5, 5.0, 1.0, 0.01
)

Ts = st.sidebar.slider(
    "Σ period",
    0.5, 5.0, 1.618, 0.001
)

plot_stride = st.sidebar.slider(
    "Plot stride (rendering performance)",
    1, 50, 1, 1,
    help="Plot every Nth point to keep large runs fast"
)

show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Core dynamics — independent clocks (NO coupling)
# ==================================================
t = np.arange(steps) * dt

Z = (t / Tz) % 1.0
S = (t / Ts) % 1.0

# Downsample for plotting only
Zp = Z[::plot_stride]
Sp = S[::plot_stride]

# ==================================================
# Plot helpers
# ==================================================
def plot_phase(Z, S):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, lw=1.1)
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
plot_phase(Zp, Sp)

if show_ts:
    st.subheader("Time Series")
    plot_timeseries(Zp, Sp)

# ==================================================
# Interpretation
# ==================================================
with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown(
        """
**What this toy demonstrates**

• Z and Σ evolve independently  
• Both variables are bounded in [0, 1]  
• The system explores a square phase space  
• No coupling, no damping, no collapse  

**Why diagonal structure may appear**

• Finite time sampling  
• Discrete dt grid  
• Rational or near-rational clock ratios  

This is expected and correct.

**Role in Sandy’s Law**

This is the **baseline trapped regime**:
- Time exists
- Motion exists
- Escape does not

All higher-order behaviour (shear, dwell, collapse)
must be compared against this reference.
"""
    )