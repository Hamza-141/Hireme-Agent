import streamlit as st
from src.ui.components import show_header, show_error, show_cv_summary

def show_upload_page():
    show_header()
    show_error()
    
    uploaded_file = st.file_uploader("Upload your CV", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if st.session_state.get("last_file") != uploaded_file.name:
            with st.spinner("Parsing CV..."):
                try:
                    from src.parsers.cv_parser import ingest
                    cv_data = ingest(uploaded_file)
                    st.session_state["cv_data"] = cv_data
                    st.session_state["last_file"] = uploaded_file.name
                except Exception as e:
                    st.session_state["error"] = f"Failed to parse CV: {str(e)}"
                    st.rerun()

    if st.session_state.get("cv_data"):
        show_cv_summary(st.session_state["cv_data"])
        
    col1, col2 = st.columns(2)
    with col1:
        loc = st.text_input("Job Location", value=st.session_state.get("location", ""))
        st.session_state["location"] = loc
    with col2:
        cnt = st.selectbox("Number of Jobs", options=[3, 5, 10], index=[3, 5, 10].index(st.session_state.get("count", 3)))
        st.session_state["count"] = cnt
        
    has_cv = st.session_state.get("cv_data") is not None
    has_loc = bool(st.session_state.get("location", "").strip())
    
    can_submit = has_cv and has_loc
    
    if st.button("Find Jobs and Write Cover Letters", type="primary", use_container_width=True, disabled=not can_submit):
        with st.spinner("Finding matches and writing cover letters. This will take 30 to 60 seconds..."):
            try:
                from src.agents.hire_agent import run_agent
                results = run_agent(st.session_state["location"], st.session_state["count"])
                st.session_state["results"] = results
                st.session_state["stage"] = "results"
                st.rerun()
            except Exception as e:
                st.session_state["error"] = f"An error occurred: {str(e)}"
                st.rerun()
                
    if not can_submit:
        missing = []
        if not has_cv:
            missing.append("upload a CV")
        if not has_loc:
            missing.append("enter a location")
        st.caption(f"Please {' and '.join(missing)} to continue.")
