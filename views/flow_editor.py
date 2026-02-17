import streamlit as st
import graphviz
from utils.storage import load_projects, update_project_data
from engine.definitions import AVAILABLE_MODELS, AVAILABLE_TOOLS
from engine.orchestrator import WorkflowEngine

def get_project(pid):
    for p in load_projects():
        if p["id"] == pid: return p
    return None

def render_editor():
    pid = st.session_state.get("current_project_id")
    project = get_project(pid)
    
    if not project:
        st.error("Project not found.")
        if st.button("Back"): st.session_state["page"] = "dashboard"; st.rerun()
        return

    # Local State
    if "nodes" not in st.session_state: st.session_state["nodes"] = project.get("nodes", [])
    if "edges" not in st.session_state: st.session_state["edges"] = project.get("edges", [])

    # Header
    c1, c2, c3 = st.columns([1, 4, 1])
    if c1.button("⬅️ خروج"): st.session_state["page"] = "dashboard"; st.rerun()
    c2.title(f"🛠️ {project['name']}")
    if c3.button("💾 حفظ", type="primary"):
        update_project_data(pid, st.session_state["nodes"], st.session_state["edges"])
        st.toast("تم الحفظ!")

    # Editor Layout
    col_viz, col_prop = st.columns([2, 1])

    with col_viz:
        st.subheader("Visual Flow")
        graph = graphviz.Digraph()
        graph.attr(rankdir='LR')
        graph.attr('node', shape='box', style='filled', fillcolor='lightblue')
        
        for n in st.session_state["nodes"]:
            graph.node(n['id'], label=f"{n['name']}\n({n['role'][:15]}...)")
        for e in st.session_state["edges"]:
            graph.edge(e['source'], e['target'])
            
        st.graphviz_chart(graph, use_container_width=True)
        
        with st.expander("➕ إضافة وكيل جديد", expanded=True):
            with st.form("add_node"):
                name = st.text_input("اسم الوكيل (مثال: Researcher)")
                if st.form_submit_button("إضافة") and name:
                    nid = name.lower().replace(" ", "_")
                    new_node = {
                        "id": nid, "name": name, 
                        "role": "You are a helpful assistant.", 
                        "model": AVAILABLE_MODELS[0], "tools": []
                    }
                    st.session_state["nodes"].append(new_node)
                    st.rerun()

    with col_prop:
        st.subheader("Properties")
        if st.session_state["nodes"]:
            names = [n["name"] for n in st.session_state["nodes"]]
            sel_name = st.selectbox("تعديل الوكيل:", names)
            node = next(n for n in st.session_state["nodes"] if n["name"] == sel_name)
            idx = st.session_state["nodes"].index(node)

            with st.container(border=True):
                node['name'] = st.text_input("الاسم", node['name'], key=f"n_{node['id']}")
                node['role'] = st.text_area("الدور", node['role'], key=f"r_{node['id']}")
                node['model'] = st.selectbox("الموديل", AVAILABLE_MODELS, index=0, key=f"m_{node['id']}")
                
                tool_ids = [t['id'] for t in AVAILABLE_TOOLS]
                node['tools'] = st.multiselect("الأدوات", tool_ids, default=node.get('tools', []), key=f"t_{node['id']}")
                
                st.session_state["nodes"][idx] = node

                st.markdown("---")
                other_ids = [n['id'] for n in st.session_state["nodes"] if n['id'] != node['id']]
                target = st.selectbox("إرسال إلى:", ["None"] + other_ids, key=f"tg_{node['id']}")
                
                if st.button("🔗 ربط", key=f"lnk_{node['id']}"):
                    if target != "None":
                        st.session_state["edges"].append({"source": node['id'], "target": target})
                        st.rerun()
                
                if st.button("🗑️ حذف الوكيل", key=f"del_{node['id']}"):
                    st.session_state["nodes"].pop(idx)
                    st.session_state["edges"] = [e for e in st.session_state["edges"] if e['source']!=node['id'] and e['target']!=node['id']]
                    st.rerun()

    # Execution Section
    st.markdown("---")
    st.subheader("▶️ تشغيل الفريق")
    api_key = st.text_input("Gemini API Key", type="password")
    user_input = st.text_area("المدخلات (المهمة):", "ابحث عن أحدث أخبار الذكاء الاصطناعي.")
    
    if st.button("🚀 ابدأ", type="primary"):
        if not api_key:
            st.error("مطلوب مفتاح API")
            return
            
        update_project_data(pid, st.session_state["nodes"], st.session_state["edges"])
        engine = WorkflowEngine(api_key, st.session_state["nodes"], st.session_state["edges"])
        
        with st.spinner("جاري العمل..."):
            res, logs = engine.execute(user_input)
            st.success("تم!")
            with st.expander("Logs"):
                for l in logs: st.text(l)
            st.info(f"النتيجة النهائية:\n{res}")
