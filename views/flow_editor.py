import streamlit as st
try:
    import graphviz
except:
    graphviz = None # Handle Android missing binary
from utils.storage import load_projects, update_project_data
from engine.definitions import AVAILABLE_MODELS, AVAILABLE_TOOLS
from engine.orchestrator import WorkflowEngine

def render_editor():
    pid = st.session_state.get("current_project_id")
    # Simple loader
    proj = next((p for p in load_projects() if p["id"] == pid), None)
    if not proj: st.error("No Project"); return

    if "nodes" not in st.session_state: st.session_state["nodes"] = proj.get("nodes", [])
    if "edges" not in st.session_state: st.session_state["edges"] = proj.get("edges", [])

    if st.button("⬅️ Back"): st.session_state["page"] = "dashboard"; st.rerun()
    st.title(f"🛠️ {proj['name']}")
    if st.button("💾 Save"):
        update_project_data(pid, st.session_state["nodes"], st.session_state["edges"])
        st.toast("Saved")

    # Visualization (Safe Mode for Android)
    st.subheader("Flow")
    if graphviz:
        try:
            g = graphviz.Digraph()
            for n in st.session_state["nodes"]: g.node(n['id'], label=n['name'])
            for e in st.session_state["edges"]: g.edge(e['source'], e['target'])
            st.graphviz_chart(g)
        except:
            st.warning("Graphviz binary missing on Android. Visualization disabled.")
    else:
        st.info("Visuals disabled (Graphviz missing). Logic still works.")

    with st.expander("Add Agent"):
        name = st.text_input("Agent Name")
        if st.button("Add") and name:
            nid = name.lower().replace(" ", "_")
            st.session_state["nodes"].append({"id": nid, "name": name, "role": "Helpful AI", "model": "gemini-1.5-flash", "tools": []})
            st.rerun()
            
    # Properties & Linking
    if st.session_state["nodes"]:
        sel = st.selectbox("Edit Agent", [n["name"] for n in st.session_state["nodes"]])
        node = next(n for n in st.session_state["nodes"] if n["name"] == sel)
        idx = st.session_state["nodes"].index(node)
        
        node['name'] = st.text_input("Name", node['name'], key=f"n_{idx}")
        node['role'] = st.text_area("Role", node['role'], key=f"r_{idx}")
        target = st.selectbox("Link To", ["None"] + [n['id'] for n in st.session_state["nodes"] if n['id'] != node['id']], key=f"t_{idx}")
        if st.button("Link", key=f"l_{idx}") and target != "None":
            st.session_state["edges"].append({"source": node['id'], "target": target})
            st.rerun()
        st.session_state["nodes"][idx] = node

    st.markdown("---")
    key = st.text_input("API Key", type="password")
    inp = st.text_input("Task", "Hello")
    if st.button("Run"):
        eng = WorkflowEngine(key, st.session_state["nodes"], st.session_state["edges"])
        res, logs = eng.execute(inp)
        st.write(res)
        st.write(logs)
