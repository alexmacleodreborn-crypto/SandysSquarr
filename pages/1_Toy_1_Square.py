import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Toy 1 — Square", layout="wide")
st.title("Toy 1 — Bounded Phase-Space Regime (Square)")
st.caption("Independent + clamped → square/box geometry in (Z, Σ).")

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def simulate_square(steps, dt, Z0, S0):
    Z, S = Z0, S0
    Zh, Sh = [], []

    for _ in range(steps):
        # Sign driver → hard edges (square)
        dZ = np.sign(0.5 - Z)
        dS = np.sign(S - 0.5)

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
    ax.set_title("Square: Independent + Clamped")
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

# Controls (defaults chosen to show square)
with st.sidebar:
    st.header("Toy 1 Controls")
    steps = st.slider("Steps", 500, 12000, 4000, 500)
    dt = st.slider("dt", 0.001, 0.05, 0.02, 0.001)
    Z0 = st.slider("Z0", 0.0, 1.0, 0.60, 0.01)
    S0 = st.slider("Σ0", 0.0, 1.0, 0.40, 0.01)
    show_ts = st.checkbox("Show Time Series", True)

Z, S = simulate_square(steps, dt, Z0, S0)

c1, c2 = st.columns([1,1])
with c1:
    plot_phase(Z, S)
with c2:
    if show_ts:
        plot_ts(Z, S)

st.info("If you don’t see a clear square: increase dt slightly (e.g. 0.02→0.03) and increase steps.")