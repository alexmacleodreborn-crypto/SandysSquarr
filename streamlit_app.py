import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Sandy’s Law — Phase Space Toys",
    layout="wide"
)

# ==================================================
# Helpers
# ==================================================

def clamp(x):
    return max(0.0, min(1.0, x))

def plot_phase(Z, S, title):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, lw=1.4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title(title)
    ax.grid(alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_ts(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("step")
    ax.legend()
    ax.grid(alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

# ==================================================
# TOY 1 — Square (Reflecting box)
# ==================================================

def toy_square(steps, dt):
    Z, S = 0.6, 0.4
    vZ, vS = 0.35, 0.22

    Zh, Sh = [], []

    for _ in range(steps):
        Z += vZ * dt
        S += vS * dt

        if Z <= 0 or Z >= 1:
            vZ *= -1
            Z = clamp(Z)

        if S <= 0 or S >= 1:
            vS *= -1
            S = clamp(S)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ==================================================
# TOY 2 — Coupled Sheared Oscillator
# ==================================================

def toy_shear(steps, dt, k, damping):
    Z, S = 0.6, 0.4
    vZ, vS = 0.0, 0.0

    Zh, Sh = [], []

    for _ in range(steps):
        aZ = -k * (Z - 0.5) + k * (S - 0.5) - damping * vZ
        aS = -k * (S - 0.5) - k * (Z - 0.5) - damping * vS

        vZ += aZ * dt
        vS += aS * dt

        Z += vZ * dt
        S += vS * dt

        Z = clamp(Z)
        S = clamp(S)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh)

# ==================================================
# TOY 3 — Corner Dwell → Collapse
# ==================================================

def toy_corner(steps, dt, drift, collapse_k, corner_th):
    Z, S = 0.6, 0.4
    vZ, vS = drift, drift * 0.7

    Zh, Sh = [], []
    dwell = 0

    def in_corner(z, s):
        return (z > corner_th and s > corner_th)

    for _ in range(steps):
        if in_corner(Z, S):
            dwell += 1
            # collapse ramps gradually
            vZ -= collapse_k * (Z - 0.5) * dt
            vS -= collapse_k * (S - 0.5) * dt

        Z += vZ * dt
        S += vS * dt

        if Z <= 0 or Z >= 1:
            vZ *= -1
        if S <= 0 or S >= 1:
            vS *= -1

        Z = clamp(Z)
        S = clamp(S)

        Zh.append(Z)
        Sh.append(S)

    return np.array(Zh), np.array(Sh), dwell / steps

# ==================================================
# UI
# ==================================================

st.sidebar.title("Toy Selector")
toy = st.sidebar.radio("Choose toy", ["Toy 1 — Square", "Toy 2 — Shear", "Toy 3 — Corner"])

steps = st.sidebar.slider("Steps", 2000, 8000, 5000, 500)
dt = st.sidebar.slider("dt", 0.005, 0.03, 0.01, 0.001)
show_ts = st.sidebar.checkbox("Show time series", True)

# ==================================================
# Run
# ==================================================

if toy == "Toy 1 — Square":
    st.header("Toy 1 — Bounded Phase Space (Square)")
    Z, S = toy_square(steps, dt)
    plot_phase(Z, S, "Square via Reflecting Boundaries")
    if show_ts:
        plot_ts(Z, S)

elif toy == "Toy 2 — Shear":
    st.header("Toy 2 — Coupled Sheared Oscillator")
    k = st.sidebar.slider("Coupling strength", 0.5, 3.0, 1.2, 0.1)
    damping = st.sidebar.slider("Damping", 0.0, 0.3, 0.05, 0.01)

    Z, S = toy_shear(steps, dt, k, damping)
    plot_phase(Z, S, "Stable Sheared Loops")
    if show_ts:
        plot_ts(Z, S)

elif toy == "Toy 3 — Corner":
    st.header("Toy 3 — Corner Dwell → Collapse")

    drift = st.sidebar.slider("Drift speed", 0.1, 0.6, 0.3, 0.05)
    collapse_k = st.sidebar.slider("Collapse strength", 0.5, 4.0, 1.5, 0.1)
    corner_th = st.sidebar.slider("Corner threshold", 0.7, 0.95, 0.85, 0.01)

    Z, S, dwell_frac = toy_corner(steps, dt, drift, collapse_k, corner_th)
    plot_phase(Z, S, "Square → Corner Dwell → Quench")
    if show_ts:
        plot_ts(Z, S)

    st.subheader("Corner Diagnostics")
    st.metric("Corner dwell fraction", f"{100*dwell_frac:.2f}%")