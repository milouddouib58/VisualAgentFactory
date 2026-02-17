import streamlit as st
from utils.storage import load_projects, update_project_data
from engine.definitions import AVAILABLE_MODELS, AVAILABLE_TOOLS
from engine.orchestrator import WorkflowEngine

# --- محاولة استيراد مكتبة الرسم بشكل آمن ---
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

def get_project_by_id(pid):
    """جلب بيانات المشروع بأمان"""
    projects = load_projects()
    # البحث عن المشروع، وإرجاع None إذا لم يوجد
    return next((p for p in projects if p["id"] == pid), None)

def render_editor():
    # 1. التحقق من وجود مشروع مفتوح
    project_id = st.session_state.get("current_project_id")
    if not project_id:
        st.warning("⚠️ لم يتم تحديد مشروع.")
        if st.button("العودة للرئيسية"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    project = get_project_by_id(project_id)
    if not project:
        st.error("❌ لم يتم العثور على المشروع في قاعدة البيانات.")
        if st.button("العودة"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    # 2. تهيئة المتغيرات المحلية (Session State)
    if "nodes" not in st.session_state:
        st.session_state["nodes"] = project.get("nodes", [])
    if "edges" not in st.session_state:
        st.session_state["edges"] = project.get("edges", [])

    # --- الشريط العلوي (Header) ---
    col_back, col_title, col_save = st.columns([1, 4, 1])
    
    with col_back:
        if st.button("⬅️ خروج"):
            st.session_state["page"] = "dashboard"
            st.rerun()
            
    with col_title:
        st.markdown(f"### 🛠️ محرر الفريق: {project['name']}")
        
    with col_save:
        if st.button("💾 حفظ", type="primary"):
            update_project_data(project_id, st.session_state["nodes"], st.session_state["edges"])
            st.toast("تم حفظ التغييرات بنجاح!", icon="✅")

    # --- واجهة المحرر (Editor UI) ---
    col_viz, col_props = st.columns([2, 1])

    # === العمود الأيسر: الرسم البياني وإضافة الوكلاء ===
    with col_viz:
        st.subheader("مخطط سير العمل (Workflow)")
        
        # منطق الرسم الآمن
        if HAS_GRAPHVIZ:
            try:
                graph = graphviz.Digraph()
                graph.attr(rankdir='LR') # من اليسار لليمين
                graph.attr('node', shape='box', style='filled', fillcolor='#e1f5fe')
                
                # رسم العقد
                for n in st.session_state["nodes"]:
                    label = f"{n['name']}\n({n['role'][:15]}...)"
                    graph.node(n['id'], label=label)
                
                # رسم الروابط
                for e in st.session_state["edges"]:
                    graph.edge(e['source'], e['target'])
                
                st.graphviz_chart(graph, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ تعذر رسم المخطط (قد يكون برنامج Graphviz غير مثبت)، لكن المنطق يعمل.")
                st.error(f"تفاصيل الخطأ: {e}")
        else:
            st.info("ℹ️ وضع النصوص فقط (Text Mode): مكتبة Graphviz غير مثبتة. يمكنك العمل بدون رسومات.")
            # عرض بديل نصي بسيط
            if st.session_state["nodes"]:
                st.write("**قائمة الوكلاء:**")
                for n in st.session_state["nodes"]:
                    st.code(f"[{n['name']}] --> {n['role']}")

        # إضافة وكيل جديد
        st.markdown("---")
        with st.expander("➕ إضافة وكيل جديد (Add Agent)", expanded=True):
            with st.form("add_agent_form"):
                new_name = st.text_input("اسم الوكيل (مثال: Researcher)")
                submitted = st.form_submit_button("إضافة")
                
                if submitted and new_name:
                    # إنشاء ID فريد وبسيط
                    new_id = new_name.lower().strip().replace(" ", "_")
                    
                    # التحقق من عدم التكرار
                    if any(n['id'] == new_id for n in st.session_state["nodes"]):
                        st.error("هذا الاسم موجود مسبقاً!")
                    else:
                        new_node = {
                            "id": new_id,
                            "name": new_name,
                            "role": "You are a helpful AI assistant.",
                            "model": AVAILABLE_MODELS[0], # الافتراضي
                            "tools": []
                        }
                        st.session_state["nodes"].append(new_node)
                        st.rerun()

    # === العمود الأيمن: خصائص الوكيل (Properties) ===
    with col_props:
        st.subheader("⚙️ خصائص الوكيل")
        
        if not st.session_state["nodes"]:
            st.info("قم بإضافة وكيل للبدء.")
        else:
            # 1. اختيار الوكيل
            node_names = [n["name"] for n in st.session_state["nodes"]]
            selected_name = st.selectbox("اختر وكيلاً للتعديل:", node_names)
            
            # العثور على الوكيل المختار
            current_node = next(n for n in st.session_state["nodes"] if n["name"] == selected_name)
            node_idx = st.session_state["nodes"].index(current_node)

            # 2. تعديل البيانات
            with st.container(border=True):
                # تعديل الاسم
                new_n_name = st.text_input("الاسم", current_node['name'], key=f"name_{current_node['id']}")
                current_node['name'] = new_n_name
                
                # تعديل الدور
                new_role = st.text_area("الدور (System Instruction)", current_node['role'], height=100, key=f"role_{current_node['id']}")
                current_node['role'] = new_role
                
                # تعديل الموديل
                new_model = st.selectbox("الموديل", AVAILABLE_MODELS, index=0, key=f"model_{current_node['id']}")
                current_node['model'] = new_model
                
                # تعديل الأدوات
                tool_options = [t['id'] for t in AVAILABLE_TOOLS]
                current_tools = current_node.get('tools', [])
                # تنظيف الأدوات القديمة في حال تغيرت القائمة
                valid_tools = [t for t in current_tools if t in tool_options]
                
                new_tools = st.multiselect("الأدوات", tool_options, default=valid_tools, key=f"tools_{current_node['id']}")
                current_node['tools'] = new_tools
                
                # حفظ التعديلات في الذاكرة المؤقتة
                st.session_state["nodes"][node_idx] = current_node

                st.markdown("---")
                # 3. الربط (Linking)
                st.write("**🔗 ربط المخرجات بـ (Connect Output To):**")
                
                # قائمة الأهداف الممكنة (كل الوكلاء ما عدا الحالي)
                potential_targets = [n for n in st.session_state["nodes"] if n['id'] != current_node['id']]
                target_options = ["None"] + [n['id'] for n in potential_targets]
                
                target_sel = st.selectbox("إرسال إلى:", target_options, key=f"target_{current_node['id']}")
                
                if st.button("إضافة رابط", key=f"btn_link_{current_node['id']}"):
                    if target_sel != "None":
                        # منع التكرار
                        if not any(e['source'] == current_node['id'] and e['target'] == target_sel for e in st.session_state["edges"]):
                            st.session_state["edges"].append({"source": current_node['id'], "target": target_sel})
                            st.rerun()

                # 4. الحذف (Delete)
                st.markdown("---")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    # حذف الروابط الخارجة من هذا الوكيل
                    if st.button("فك الارتباط", key=f"unlink_{current_node['id']}"):
                         st.session_state["edges"] = [e for e in st.session_state["edges"] if e['source'] != current_node['id']]
                         st.rerun()
                with col_d2:
                    # حذف الوكيل نفسه
                    if st.button("🗑️ حذف الوكيل", key=f"del_{current_node['id']}", type="primary"):
                        st.session_state["nodes"].pop(node_idx)
                        # تنظيف الروابط المتعلقة به
                        st.session_state["edges"] = [e for e in st.session_state["edges"] if e['source'] != current_node['id'] and e['target'] != current_node['id']]
                        st.rerun()

    # --- منطقة التشغيل (Execution Area) ---
    st.markdown("---")
    st.subheader("▶️ تشغيل الفريق (Execution)")
    
    with st.container(border=True):
        col_key, col_input = st.columns([1, 2])
        
        with col_key:
            api_key = st.text_input("Gemini API Key", type="password", help="احصل عليه من aistudio.google.com")
        
        with col_input:
            user_task = st.text_area("المهمة المطلوبة (Prompt):", "مثال: ابحث عن تاريخ الذكاء الاصطناعي ولخصه.")

        if st.button("🚀 ابدأ التنفيذ", use_container_width=True, type="primary"):
            if not api_key:
                st.error("⚠️ يجب إدخال مفتاح API Key للعمل.")
            elif not st.session_state["nodes"]:
                st.error("⚠️ لا يوجد وكلاء في الفريق! أضف وكيلاً واحداً على الأقل.")
            else:
                # حفظ التغييرات قبل التشغيل لضمان التزامن
                update_project_data(project_id, st.session_state["nodes"], st.session_state["edges"])
                
                # تهيئة المحرك
                engine = WorkflowEngine(
                    api_key=api_key,
                    nodes=st.session_state["nodes"],
                    edges=st.session_state["edges"]
                )
                
                # عرض النتائج
                result_placeholder = st.empty()
                logs_expander = st.expander("سجل العمليات (Live Logs)", expanded=True)
                
                with st.spinner("جاري تشغيل الوكلاء..."):
                    try:
                        final_res, logs = engine.execute(user_task)
                        
                        # تحديث السجلات
                        with logs_expander:
                            for log in logs:
                                st.text(log)
                        
                        if "Error" in str(final_res) and len(str(final_res)) < 100:
                            st.error(f"حدث خطأ: {final_res}")
                        else:
                            st.success("✅ تمت المهمة بنجاح!")
                            st.markdown("### النتيجة النهائية:")
                            st.markdown(final_res)
                            
                    except Exception as e:
                        st.error(f"حدث خطأ غير متوقع أثناء التنفيذ: {e}")

