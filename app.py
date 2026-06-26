"""HireMe Agent – Streamlit application entry point."""

import streamlit as st
from src.ui.upload_page import show_upload_page
from src.ui.results_page import show_results_page

st.set_page_config(
    page_title="HireMe Agent",
    page_icon="💼",
    layout="centered",
)

# ── Initialise session state with defaults ──────────────────────────────────
_defaults = {
    "stage": "upload",
    "cv_data": None,
    "results": [],
    "location": "",
    "count": 3,
    "error": None,
    "last_file": None,
}

for key, value in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Route to the correct page ───────────────────────────────────────────────
if st.session_state.stage == "results":
    show_results_page()
else:
    show_upload_page()

# Trigger reload
