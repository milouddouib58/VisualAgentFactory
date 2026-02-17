import streamlit as st
from utils.storage import load_projects, save_project, delete_project

def render_dashboard():
    st.title("🏭 Visual Agent Factory")
    with st.sidebar.form("new"):
        name = st.text_input("Name")
        desc = st.text_input("Desc")
        if st.form_submit_button("Create") and name:
            save_project(name, desc)
            st.rerun()
            
    for p in load_projects():
        with st.container(border=True):
            st.subheader(p["name"])
            c1, c2 = st.columns(2)
            if c1.button("Open", key=f"op_{p['id']}"):
                st.session_state["current_project_id"] = p["id"]
                st.session_state["page"] = "editor"
                st.rerun()
            if c2.button("Delete", key=f"del_{p['id']}"):
                delete_project(p["id"])
                st.rerun()
