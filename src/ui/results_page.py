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
            
            company = res.get("company", "Unknown Company")
            location = res.get("location", "Unknown Location")
            salary = res.get("salary", "Not specified")
            st.write(f"🏢 **{company}** | 📍 {location} | 💰 {salary}")
            
            job_url = res.get("job_url", "#")
            st.link_button("View Job Posting", job_url)
            
            with st.expander("📝 View / Edit Cover Letter"):
                cl_text = res.get("cover_letter", "")
                text_key = f"cl_{idx}"
                edited_text = st.text_area("Cover Letter", value=cl_text, height=300, key=text_key, label_visibility="collapsed")
                # Using a regular button for copy, as Streamlit doesn't have a native clipboard copy action without workarounds.
                # In Streamlit >= 1.30, st.code can be used, but since it's a text area, we just provide a copy hint.
                if st.button("Copy to Clipboard", key=f"copy_{idx}"):
                    st.toast("Please copy the text manually from the text area above.", icon="ℹ️")
                    
            st.divider()
            
    st.caption("Powered by GPT-4o, Adzuna, and Streamlit.")
