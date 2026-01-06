import streamlit as st

st.set_page_config(
    page_title="Sandy’s Law — Toys",
    layout="wide"
)

st.title("Sandy’s Law — Toy Suite (Separated Pages)")
st.caption("Each toy is isolated on its own page to prevent cross-breakage.")

st.markdown(
"""
## What this app contains

- **Toy 1 — BPSR Square (independent + clamped)**  
- **Toy 2 — Coupled System (square shears / loops)**  
- **Toy 3 — Edge Lock → Corner Collapse (with dwell diagnostics)**  

Use the sidebar to switch pages.

### Rule
We do not share code paths that change a toy’s behavior while editing another toy.
"""
)