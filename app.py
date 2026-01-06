import streamlit as st

st.set_page_config(
    page_title="Sandy’s Law Toy Suite",
    layout="wide"
)

st.title("Sandy’s Law — Toy System Suite")
st.caption("Phase-space diagnostics for bounded, coupled, and collapsed regimes.")

st.markdown("""
### Select a Toy Model (via sidebar)
1. **Toy 1 — Square Phase Traversal**  
   Independent Z–Σ oscillators bounded in phase space.

2. **Toy 2 — Closed Loop System**  
   Exact conservative rotation (no numerical energy injection).

3. **Toy 3 — Corner Dwell → Quench**  
   Controlled collapse regime with measurable dwell fraction.
""")

st.info("Navigate using the left sidebar to open each toy module.")