import streamlit as st
from src.ui.components import show_header, show_error
from src.memory.cv_store import clear_cv

def show_results_page():
    show_header()
    show_error()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Your Tailored Job Matches")
    with col2:
        if st.button("Start Over", use_container_width=True):
            clear_cv()
            st.session_state["cv_data"] = None
            st.session_state["results"] = []
            st.session_state["last_file"] = None
            st.session_state["error"] = None
            st.session_state["stage"] = "upload"
            st.rerun()

    results = st.session_state.get("results", [])
    if not results:
        st.warning("No results found. Try adjusting your search criteria.")
        return

    for idx, res in enumerate(results):
        with st.container():
            st.subheader(res.get("job_title", "Unknown Title"))

            company  = res.get("company", "Unknown Company")
            location = res.get("location", "Unknown Location")
            salary   = res.get("salary", "Not specified")
            contract = res.get("contract", "")
            posted   = res.get("posted", "")

            # Main info line
            st.write(f"🏢 **{company}** | 📍 {location} | 💰 {salary}")

            # Secondary info line (only show fields that have values)
            secondary = []
            if contract and contract != "Not specified":
                secondary.append(f"📋 {contract}")
            if posted and posted != "Unknown":
                secondary.append(f"📅 Posted {posted}")
            if secondary:
                st.caption("  ·  ".join(secondary))

            job_url = res.get("job_url", "#")
            if job_url and job_url != "#":
                st.link_button("🔗 View Original Job Posting →", job_url)
            else:
                st.caption("_(Job link unavailable)_")

            with st.expander("📝 View / Edit Cover Letter"):
                cl_text = res.get("cover_letter", "")
                text_key = f"cl_{idx}"
                st.text_area(
                    "Cover Letter",
                    value=cl_text,
                    height=300,
                    key=text_key,
                    label_visibility="collapsed"
                )
                if st.button("Copy to Clipboard", key=f"copy_{idx}"):
                    st.toast("Please copy the text manually from the text area above.", icon="ℹ️")

            st.divider()

    st.caption("Powered by Groq (Llama 3.3), Adzuna, and Streamlit.")

