import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Toy 2 — Coupled", layout="wide")
st.title("Toy 2 — Coupled System (Square Shears / Loops)")
st.caption("Coupling between Z and Σ breaks the square and creates tilted loops.")

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def simulate_coupled(steps, dt, Z0, S0, k_zs, k_sz):
    Z, S = Z0, S0
    Zh, Sh = [], []

    for _ in range(steps):
        # Base square driver (sign)
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)

        # Coupling (your original form)
        dZ += k_zs * (S - 0.5)
        dS += k_sz * (Z - 0.5)

        Z = clamp(Z + dt * dZ)
        S = clamp(S + dt * dS)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

def plot_phase(Z, S):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.plot(Z, S, lw=1.3)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.35)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title("Coupled: Geometry Tilts / Breaks")
    st.pyplot(fig); plt.close(fig)

def plot_ts(Z, S):
    fig, ax = plt.subplots(figsize=(7,3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.grid(True, alpha=0.35)
    ax.set_xlabel("step"); ax.set_ylabel("value")
    ax.set_title("Time Series")
    ax.legend()
    st.pyplot(fig); plt.close(fig)

with st.sidebar:
    st.header("Toy 2 Controls")
    steps = st.slider("Steps", 500, 12000, 5000, 500)
    dt = st.slider("dt", 0.001, 0.05, 0.03, 0.001)
    Z0 = st.slider("Z0", 0.0, 1.0, 0.60, 0.01)
    S0 = st.slider("Σ0", 0.0, 1.0, 0.40, 0.01)
    k_zs = st.slider("k_ZΣ (Σ→Z)", -3.0, 3.0, 1.5, 0.1)
    k_sz = st.slider("k_ΣZ (Z→Σ)", -3.0, 3.0, -1.2, 0.1)
    show_ts = st.checkbox("Show Time Series", True)

Z, S = simulate_coupled(steps, dt, Z0, S0, k_zs, k_sz)

c1, c2 = st.columns([1,1])
with c1:
    plot_phase(Z, S)
with c2:
    if show_ts:
        plot_ts(Z, S)

st.success("This is the 'working Toy 2' regime: coupling breaks the square and produces tilted loops.")