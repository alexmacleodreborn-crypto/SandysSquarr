import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="Toy 2 — Coupled Shear Loops",
    layout="wide"
)

st.title("Toy 2 — Coupled System (Sheared Loops)")
st.caption("Pure coupling → closed loops (area-preserving). No damping, no collapse.")

# ==================================================
# Sidebar controls
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider("Steps", 1000, 50000, 15000, 1000)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)

omega = st.sidebar.slider("Coupling ω (loop speed)", 0.1, 10.0, 2.5, 0.1)
shear = st.sidebar.slider("Shear factor (tilt)", -3.0, 3.0, 1.0, 0.1)

kick = st.sidebar.slider("Initial kick (amplitude)", 0.0, 0.5, 0.15, 0.01)

plot_stride = st.sidebar.slider(
    "Plot stride (rendering performance)",
    1, 50, 1, 1
)

show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Core dynamics — conservative coupled rotation + shear
# ==================================================
# We evolve around center (0.5, 0.5) using a skew-symmetric field:
# dZ =  ω*(Σ-0.5)
# dΣ = -ω*(Z-0.5)
# Then apply shear by mixing the coordinates.

Z = 0.5 + kick
S = 0.5

Zh, Sh = [], []

for _ in range(steps):
    zc = Z - 0.5
    sc = S - 0.5

    # Apply shear in the state (tilt the loops)
    zc_s = zc + shear * sc
    sc_s = sc

    # Skew-symmetric coupling (pure rotation)
    dZ = omega * sc_s
    dS = -omega * zc_s

    Z = Z + dt * dZ
    S = S + dt * dS

    # Soft clamp to [0,1] just for display stability (shouldn't hit bounds)
    Z = max(0.0, min(1.0, Z))
    S = max(0.0, min(1.0, S))

    Zh.append(Z)
    Sh.append(S)

Z_arr = np.array(Zh)
S_arr = np.array(Sh)

# Downsample for plotting
Zp = Z_arr[::plot_stride]
Sp = S_arr[::plot_stride]

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
    ax.set_title("Phase Space: Stable Sheared Loops")
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series (Coupled Loops)")
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

• Z and Σ are now **coupled**  
• The system no longer fills a square — it forms **closed loops**  
• Loops represent **time-unlocked oscillatory evolution**  
• No damping here: loops do not spiral inward  

**How to read the controls**

• **ω** sets the speed around the loop  
• **Shear** tilts the loop geometry  
• **Kick** sets the initial loop radius  

This is the minimal deterministic “shear-unlock” regime.
"""
    )