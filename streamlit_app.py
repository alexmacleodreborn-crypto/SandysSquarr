import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sandy’s Law Toys — Robust", layout="wide")
st.title("Sandy’s Law — Toy Suite (Robust)")
st.caption("No sign+clamp brittleness. Uses smooth drift + reflecting boundaries.")

# ----------------------------
# Helpers
# ----------------------------
def reflect01(x: float) -> float:
    # Reflecting boundary on [0,1]
    # If x < 0 -> -x ; if x > 1 -> 2-x ; repeat if dt is huge
    while x < 0 or x > 1:
        if x < 0:
            x = -x
        elif x > 1:
            x = 2 - x
    return x

def plot_phase(Z, S, title, corner_th=None):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, lw=1.3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.35)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title(title)

    if corner_th is not None:
        th = corner_th
        # draw corner boxes (visual aid)
        ax.axvline(th, lw=0.8, alpha=0.3)
        ax.axhline(th, lw=0.8, alpha=0.3)
        ax.axvline(1-th, lw=0.8, alpha=0.3)
        ax.axhline(1-th, lw=0.8, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

def plot_ts(Z, S):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.set_xlabel("step")
    ax.set_ylabel("value")
    ax.set_title("Time Series")
    ax.grid(True, alpha=0.35)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

def corner_mask(Z, S, th):
    Z = np.asarray(Z); S = np.asarray(S)
    return ((Z > th) & (S > th)) | ((Z < 1-th) & (S < 1-th))

# ----------------------------
# Toy 1: Square (robust)
# ----------------------------
def run_toy1(steps, dt, vZ, vS, Z0, S0):
    # constant drift directions -> makes rectangular traversal with reflections
    Z, S = Z0, S0
    Zh, Sh = [], []
    for _ in range(steps):
        Z = reflect01(Z + dt * vZ)
        S = reflect01(S + dt * vS)
        Zh.append(Z); Sh.append(S)
    return np.array(Zh), np.array(Sh)

# ----------------------------
# Toy 2: Coupled (stable shear / loops)
# ----------------------------
def run_toy2(steps, dt, a, b, Z0, S0):
    # Linear coupled oscillator around (0.5,0.5) with reflection
    Z, S = Z0, S0
    Zh, Sh = [], []
    for _ in range(steps):
        x = Z - 0.5
        y = S - 0.5

        # rotation + mild restoring -> stable loops
        dZ = -a * x + b * y
        dS = -a * y - b * x

        Z = reflect01(Z + dt * dZ)
        S = reflect01(S + dt * dS)

        Zh.append(Z); Sh.append(S)
    return np.array(Zh), np.array(Sh)

# ----------------------------
# Toy 3: Square -> corner dwell -> collapse
# ----------------------------
def run_toy3(steps, dt, vZ, vS, th, collapse_quench, Z0, S0):
    # Same square drift as Toy 1, but when in corner, motion is quenched (slows)
    Z, S = Z0, S0
    Zh, Sh = [], []
    hits = []
    for _ in range(steps):
        in_c = (Z > th and S > th) or (Z < 1-th and S < 1-th)
        hits.append(1 if in_c else 0)

        q = (1.0 - collapse_quench) if in_c else 1.0  # quench reduces speed
        Z = reflect01(Z + dt * (vZ * q))
        S = reflect01(S + dt * (vS * q))

        Zh.append(Z); Sh.append(S)
    return np.array(Zh), np.array(Sh), np.array(hits)

# ----------------------------
# UI
# ----------------------------
toy = st.sidebar.radio("Toy", ["Toy 1 — Square", "Toy 2 — Coupled Loops", "Toy 3 — Corner Dwell/Collapse"])
steps = st.sidebar.slider("Steps", 500, 15000, 6000, 500)
dt = st.sidebar.slider("dt", 0.001, 0.05, 0.02, 0.001)
Z0 = st.sidebar.slider("Z0", 0.0, 1.0, 0.60, 0.01)
S0 = st.sidebar.slider("Σ0", 0.0, 1.0, 0.40, 0.01)
show_ts = st.sidebar.checkbox("Show time series", True)

if toy == "Toy 1 — Square":
    st.subheader("Toy 1 — Square (robust)")
    st.caption("Constant drift + reflecting boundaries → always produces a box-like traversal.")
    vZ = st.sidebar.slider("vZ", -2.0, 2.0, 1.0, 0.1)
    vS = st.sidebar.slider("vΣ", -2.0, 2.0, 0.8, 0.1)

    Z, S = run_toy1(steps, dt, vZ, vS, Z0, S0)
    plot_phase(Z, S, "Toy 1: Square via Reflecting Boundaries")
    if show_ts:
        plot_ts(Z, S)

elif toy == "Toy 2 — Coupled Loops":
    st.subheader("Toy 2 — Coupled Loops (stable)")
    st.caption("Coupled linear oscillator around (0.5,0.5) + reflecting boundaries.")
    a = st.sidebar.slider("restore a", 0.0, 3.0, 0.3, 0.05)
    b = st.sidebar.slider("couple b", 0.0, 6.0, 3.0, 0.1)

    Z, S = run_toy2(steps, dt, a, b, Z0, S0)
    plot_phase(Z, S, "Toy 2: Stable Sheared Loops")
    if show_ts:
        plot_ts(Z, S)

else:
    st.subheader("Toy 3 — Corner Dwell / Collapse (robust)")
    st.caption("Square drift + corner quench → measurable dwell + controlled collapse behaviour.")
    vZ = st.sidebar.slider("vZ", -2.0, 2.0, 1.0, 0.1)
    vS = st.sidebar.slider("vΣ", -2.0, 2.0, 1.0, 0.1)
    th = st.sidebar.slider("corner threshold", 0.70, 0.95, 0.85, 0.01)
    collapse_quench = st.sidebar.slider("collapse quench", 0.0, 0.95, 0.5, 0.05)

    Z, S, hits = run_toy3(steps, dt, vZ, vS, th, collapse_quench, Z0, S0)
    plot_phase(Z, S, "Toy 3: Square → Corner Dwell → Quenched Motion", corner_th=th)
    if show_ts:
        plot_ts(Z, S)

    dwell_steps = int(hits.sum())
    dwell_time = dwell_steps * dt
    dwell_frac = dwell_steps / len(hits)

    st.markdown("### 🔴 Corner Dwell Diagnostics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Corner steps", f"{dwell_steps}")
    c2.metric("Corner dwell time", f"{dwell_time:.3f}")
    c3.metric("Corner dwell fraction", f"{100*dwell_frac:.2f}%")

    if dwell_frac < 0.05:
        st.success("Stable / Persistent")
    elif dwell_frac < 0.15:
        st.warning("Pre-instability")
    else:
        st.error("Imminent collapse")