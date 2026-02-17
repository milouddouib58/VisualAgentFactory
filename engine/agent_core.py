import google.generativeai as genai
from engine.tools_library import TOOL_FUNCTIONS

class AtomicAgent:
    def __init__(self, api_key, name, role, model_name, tool_ids):
        self.name = name
        self.role = role
        self.model = None
        try:
            genai.configure(api_key=api_key)
            tools = [TOOL_FUNCTIONS[tid] for tid in tool_ids if tid in TOOL_FUNCTIONS]
            self.model = genai.GenerativeModel(model_name=model_name, tools=tools if tools else None, system_instruction=role)
        except: pass

    def run(self, input_data):
        if not self.model: return "Error: Model not init"
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            return chat.send_message(f"Input: {input_data}").text
        except Exception as e: return f"Error: {str(e)}"
