import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# Page config
# ==================================================
st.set_page_config(
    page_title="Toy 2 — Coupled Sheared Loops (Exact)",
    layout="wide"
)

st.title("Toy 2 — Coupled System (Exact Closed Loops)")
st.caption("Exact conservative rotation · no numerical energy injection")

# ==================================================
# Sidebar
# ==================================================
st.sidebar.header("Controls")

steps = st.sidebar.slider("Steps", 1000, 50000, 20000, 1000)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.01, 0.001)

omega = st.sidebar.slider("ω (loop frequency)", 0.1, 20.0, 4.0, 0.1)
kickZ = st.sidebar.slider("Initial Z offset", -0.45, 0.45, 0.18, 0.01)
kickS = st.sidebar.slider("Initial Σ offset", -0.45, 0.45, 0.00, 0.01)

shear = st.sidebar.slider("Shear (visual only)", -3.0, 3.0, 1.0, 0.1)
stride = st.sidebar.slider("Plot stride", 1, 50, 2, 1)

show_ts = st.sidebar.checkbox("Show Time Series", True)

# ==================================================
# Exact coupled dynamics (NO DRIFT)
# ==================================================
Z = 0.5 + kickZ
S = 0.5 + kickS

Zh, Sh = [], []

theta = omega * dt
c, s = np.cos(theta), np.sin(theta)

for _ in range(steps):
    zc = Z - 0.5
    sc = S - 0.5

    # exact rotation
    zc_new =  c * zc + s * sc
    sc_new = -s * zc + c * sc

    Z = zc_new + 0.5
    S = sc_new + 0.5

    Zh.append(Z)
    Sh.append(S)

Z = np.array(Zh)
S = np.array(Sh)

# ==================================================
# Plot-only shear transform
# ==================================================
zc = Z - 0.5
sc = S - 0.5

Zp = np.clip(zc + shear * sc + 0.5, 0, 1)[::stride]
Sp = np.clip(sc + 0.5, 0, 1)[::stride]

# ==================================================
# Plots
# ==================================================
fig, ax = plt.subplots(figsize=(5, 5))
ax.plot(Zp, Sp, lw=1.2)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("equal")
ax.set_xlabel("Z (trap strength)")
ax.set_ylabel("Σ (entropy escape)")
ax.set_title("Phase Space: Exact Closed Loop (Sheared View)")
ax.grid(True, alpha=0.4)
st.pyplot(fig)
plt.close(fig)

if show_ts:
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z[::stride], label="Z")
    ax.plot(S[::stride], label="Σ")
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title("Time Series (Exact Conservative Motion)")
    ax.legend()
    ax.grid(True, alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# Diagnostics
# ==================================================
amp = np.sqrt((Z - 0.5)**2 + (S - 0.5)**2)
st.markdown("### Diagnostics")
st.metric("Amplitude (start)", f"{amp[0]:.6f}")
st.metric("Amplitude (end)", f"{amp[-1]:.6f}")

# ==================================================
# Interpretation
# ==================================================
with st.expander("Physical Interpretation (Sandy’s Law)"):
    st.markdown(
        """
• Pure Z–Σ coupling unlocks time  
• Motion is conservative (no decay, no growth)  
• Loops are *exact invariants*  
• Shear tilts geometry but does not change physics  

This is the **canonical time-unlocked regime**.
"""
    )