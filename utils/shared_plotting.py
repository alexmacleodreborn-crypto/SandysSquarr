import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def clamp(x, lo=0, hi=1):
    return max(lo, min(hi, x))

def plot_phase(Z, S, title):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(Z, S, linewidth=1.2)
    ax.set_xlabel("Z (trap strength)")
    ax.set_ylabel("Σ (entropy escape)")
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)

def plot_timeseries(Z, S, title="Time Series"):
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(Z, label="Z")
    ax.plot(S, label="Σ")
    ax.legend()
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.set_title(title)
    ax.grid(alpha=0.4)
    st.pyplot(fig)
    plt.close(fig)