from engine.agent_core import AtomicAgent
import time

class WorkflowEngine:
    def __init__(self, api_key, nodes, edges):
        self.api_key = api_key
        # تحويل القائمة إلى قاموس للوصول السريع
        self.nodes_config = {n["id"]: n for n in nodes}
        self.edges = edges
        self.logs = []

    def find_start_node(self):
        # البحث عن العقدة التي ليس لها مدخلات
        target_ids = {e["target"] for e in self.edges}
        start_nodes = [n["id"] for n in self.nodes_config.values() if n["id"] not in target_ids]
        return start_nodes[0] if start_nodes else None

    def get_next_node(self, current_id):
        for edge in self.edges:
            if edge["source"] == current_id:
                return edge["target"]
        return None

    def execute(self, initial_input):
        self.logs = []
        current_node_id = self.find_start_node()
        
        if not current_node_id:
            return "Error: No start node found.", ["Error: Disconnected graph."]

        current_input = initial_input
        steps = 0
        
        while current_node_id and steps < 10:
            node_data = self.nodes_config[current_node_id]
            
            log_msg = f"Step {steps+1}: Running Agent '{node_data['name']}'..."
            self.logs.append(log_msg)
            
            # تشغيل الوكيل
            agent = AtomicAgent(
                api_key=self.api_key,
                name=node_data["name"],
                role=node_data["role"],
                model_name=node_data["model"],
                tool_ids=node_data.get("tools", [])
            )
            
            output = agent.run(current_input)
            self.logs.append(f"Output: {output[:100]}...")
            
            # التجهيز للخطوة التالية
            current_input = output
            current_node_id = self.get_next_node(current_node_id)
            steps += 1
            time.sleep(1) # استراحة بسيطة

        return current_input, self.logs
