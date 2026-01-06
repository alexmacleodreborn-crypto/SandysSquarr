import streamlit as st

st.set_page_config(
    page_title="Sandy’s Law — Phase Space Toys",
    layout="wide",
)

st.title("Sandy’s Law — Phase Space Toys")
st.caption("Trap → Transition → Escape | deterministic toy diagnostics")

st.markdown(
    """
Use the pages in the sidebar:

- **Toy 1 — Square traversal**: independent clocks + reflecting boundaries (baseline trapped regime).
- **Toy 2 — Coupled closed loops**: exact conservative rotation + optional shear (stable loops; no blow-up).
- **Toy 3 — Corner dwell → quench**: Toy 2 base + corner capture + controlled quench + dwell diagnostics.
"""
)

st.info(
    "If you ever see Toy 2 values exploding to huge numbers, that’s numerical energy injection. "
    "This rebuild removes that by using an exact rotation update."
)