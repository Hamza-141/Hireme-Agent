import streamlit as st

def show_header():
    """Displays the app title, a short tagline, and a divider."""
    st.title("💼 HireMe Agent")
    st.markdown("Your AI-powered job hunting assistant.")
    st.divider()

def show_error():
    """Checks for errors in session state and displays them."""
    if st.session_state.get("error"):
        st.error(st.session_state["error"])
        if st.button("Dismiss"):
            st.session_state["error"] = None
            st.rerun()

def show_cv_summary(cv_data: dict):
    """Shows parsed CV data inside a collapsed expander."""
    with st.expander("📄 CV Successfully Parsed", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Name:** {cv_data.get('name', 'N/A')}")
            st.markdown(f"**Email:** {cv_data.get('email', 'N/A')}")
            st.markdown(f"**Location:** {cv_data.get('location', 'N/A')}")
            
        with col2:
            st.markdown("**Top Skills:**")
            skills = cv_data.get('skills', [])
            st.markdown(", ".join(skills[:5]) if skills else "N/A")
            
            st.markdown("**Preferred Roles:**")
            roles = cv_data.get('preferred_roles', [])
            st.markdown(", ".join(roles[:3]) if roles else "N/A")
