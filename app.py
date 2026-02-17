import streamlit as st
from views.dashboard import render_dashboard
from views.flow_editor import render_editor

st.set_page_config(page_title="Visual Agent Factory", layout="wide")

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"
if "current_project_id" not in st.session_state:
    st.session_state["current_project_id"] = None

def main():
    if st.session_state["page"] == "dashboard":
        render_dashboard()
    elif st.session_state["page"] == "editor":
        render_editor()

if __name__ == "__main__":
    main()
