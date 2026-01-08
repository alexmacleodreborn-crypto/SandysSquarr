# phase_square_coherence.py
# Sandy’s Law — Phase Coherence Instrument
# Phase geometry only • No time • No order • No dynamics

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib.colors import ListedColormap

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(
    page_title="Sandy’s Law — Phase Coherence Square",
    layout="wide"
)

st.title("Sandy’s Law — Phase Coherence Instrument")
st.caption(
    "Phase geometry only • No time • Order carries no physics • "
    "Coherence arises from phase crowding"
)

# -------------------------------------------------
# CSV input
# -------------------------------------------------
with st.expander("CSV format", expanded=False):
    st.code(
        "z,sigma\n"
        "0.46,0.27\n"
        "0.90,0.03\n"
        "...\n\n"
        "z     = trap strength proxy ∈ [0,1]\n"
        "sigma = escape proxy ∈ [0,1]\n"
        "Each row = one unordered phase event"
    )

uploaded = st.file_uploader("Upload CSV", type=["csv"])
pasted = st.text_area("…or paste CSV here", height=180)

# -------------------------------------------------
# Load data
# -------------------------------------------------
raw = None
if uploaded is not None:
    raw = uploaded.read().decode("utf-8", errors="ignore")
elif pasted.strip():
    raw = pasted

if raw is None:
    st.info("Upload or paste a CSV to begin.")
    st.stop()

try:
    df = pd.read_csv(StringIO(raw))
except Exception as e:
    st.error(f"CSV parse error: {e}")
    st.stop()

if not {"z", "sigma"}.issubset(df.columns):
    st.error("CSV must contain columns: z, sigma")
    st.stop()

df = df[["z", "sigma"]].copy()
df["z"] = pd.to_numeric(df["z"], errors="coerce")
df["sigma"] = pd.to_numeric(df["sigma"], errors="coerce")
df = df.dropna()

n_events = len(df)
if n_events < 3:
    st.warning("Very small event count — coherence may be unstable.")

# -------------------------------------------------
# Controls
# -------------------------------------------------
st.subheader("Phase Geometry Controls")

colA, colB = st.columns(2)

with colA:
    bins = st.slider("Square resolution (bins per axis)", 4, 40, 16)
with colB:
    min_shared = st.slider(
        "Minimum events per square to count as coherent",
        2, 10, 2
    )

# -------------------------------------------------
# Phase binning
# -------------------------------------------------
# Clip to [0,1] just in case
z = np.clip(df["z"].to_numpy(), 0, 1)
s = np.clip(df["sigma"].to_numpy(), 0, 1)

# Bin indices
z_bin = np.floor(z * bins).astype(int)
s_bin = np.floor(s * bins).astype(int)

# Edge safety
z_bin[z_bin == bins] = bins - 1
s_bin[s_bin == bins] = bins - 1

df["z_bin"] = z_bin
df["s_bin"] = s_bin

# Count events per square
counts = {}
for zb, sb in zip(z_bin, s_bin):
    counts[(zb, sb)] = counts.get((zb, sb), 0) + 1

# Mark coherent events
coherent_mask = np.array(
    [counts[(zb, sb)] >= min_shared for zb, sb in zip(z_bin, s_bin)]
)

df["coherent"] = coherent_mask

# -------------------------------------------------
# Coherence metric (core result)
# -------------------------------------------------
shared_events = int(coherent_mask.sum())
C = shared_events / n_events if n_events > 0 else 0.0

# Regime classification
if C >= 0.8:
    regime = "Strong macroscopic coherence (Locked)"
elif C >= 0.4:
    regime = "Transitional / mixed regime"
else:
    regime = "Free / incoherent regime"

# -------------------------------------------------
# Build square grid for visualisation
# -------------------------------------------------
grid = np.zeros((bins, bins))

for (zb, sb), cnt in counts.items():
    if cnt >= min_shared:
        grid[sb, zb] = 2      # coherent square
    else:
        grid[sb, zb] = 1      # occupied but isolated

# -------------------------------------------------
# Visualisation
# -------------------------------------------------
cmap = ListedColormap([
    "#ffffff",  # empty
    "#bfc5cc",  # isolated
    "#3fbf6f"   # coherent
])

fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(grid, origin="lower", cmap=cmap)
ax.set_title("Phase Square Projection")
ax.set_xlabel("z (trap strength)")
ax.set_ylabel("sigma (escape)")
ax.set_xticks([])
ax.set_yticks([])
plt.tight_layout()

# -------------------------------------------------
# Output
# -------------------------------------------------
left, right = st.columns([0.55, 0.45])

with left:
    st.pyplot(fig)

with right:
    st.subheader("Coherence Diagnostics")
    st.metric("Event count", n_events)
    st.metric("Shared events", shared_events)
    st.metric("Coherence C", f"{C:.3f}")
    st.markdown(f"**Regime:** {regime}")

    st.markdown("---")
    st.markdown(
        """
**Interpretation**
- Coherence does **not** imply simultaneity  
- Order is irrelevant  
- Time-like behaviour is **emergent**, not assumed  

**Sandy’s Law:**  
Trap → Transition → Escape
"""
    )

# -------------------------------------------------
# Table + download
# -------------------------------------------------
st.subheader("Event Table (Phase Only)")
st.dataframe(df, use_container_width=True)

csv_out = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download processed CSV",
    csv_out,
    file_name="phase_square_processed.csv",
    mime="text/csv"
)

st.caption("This instrument intentionally contains no time, ordering, or dynamics.")