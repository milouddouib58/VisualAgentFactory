import streamlit as st
from utils.storage import load_projects, save_project, delete_project

def render_dashboard():
    st.title("🏭 Visual Agent Factory")
    st.markdown("### منصة بناء فرق الوكلاء الذكية")
    
    with st.sidebar:
        st.header("مشروع جديد")
        with st.form("new_proj"):
            name = st.text_input("اسم الفريق")
            desc = st.text_area("الوصف")
            if st.form_submit_button("إنشاء"):
                if name:
                    save_project(name, desc)
                    st.success("تم!")
                    st.rerun()

    projects = load_projects()
    if not projects:
        st.info("لا توجد مشاريع. أنشئ واحداً من القائمة الجانبية.")
    else:
        cols = st.columns(3)
        for i, p in enumerate(projects):
            with cols[i%3]:
                with st.container(border=True):
                    st.subheader(p["name"])
                    st.caption(p["created_at"])
                    st.write(p["description"] or "...")
                    c1, c2 = st.columns(2)
                    if c1.button("🚀 فتح", key=f"open_{p['id']}"):
                        st.session_state["current_project_id"] = p["id"]
                        st.session_state["page"] = "editor"
                        st.rerun()
                    if c2.button("🗑️ حذف", key=f"del_{p['id']}"):
                        delete_project(p["id"])
                        st.rerun()
