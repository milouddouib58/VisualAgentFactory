from engine.agent_core import AtomicAgent
import time

class WorkflowEngine:
    def __init__(self, api_key, nodes, edges):
        self.api_key = api_key
        self.nodes_config = {n["id"]: n for n in nodes}
        self.edges = edges
        self.logs = []

    def find_start_node(self):
        target_ids = {e["target"] for e in self.edges}
        start_nodes = [n["id"] for n in self.nodes_config.values() if n["id"] not in target_ids]
        return start_nodes[0] if start_nodes else None

    def get_next_node(self, current_id):
        for edge in self.edges:
            if edge["source"] == current_id: return edge["target"]
        return None

    def execute(self, initial_input):
        self.logs = []
        curr = self.find_start_node()
        if not curr: return "No start node", []
        
        inp = initial_input
        steps = 0
        while curr and steps < 10:
            nd = self.nodes_config[curr]
            self.logs.append(f"Step {steps+1}: {nd['name']}...")
            agent = AtomicAgent(self.api_key, nd['name'], nd['role'], nd['model'], nd.get('tools', []))
            inp = agent.run(inp)
            self.logs.append(f"Output: {inp[:50]}...")
            curr = self.get_next_node(curr)
            steps += 1
            time.sleep(1)
        return inp, self.logs
