import google.generativeai as genai
from engine.tools_library import TOOL_FUNCTIONS

class AtomicAgent:
    def __init__(self, api_key, name, role, model_name, tool_ids):
        self.name = name
        self.role = role
        self.model_name = model_name
        
        genai.configure(api_key=api_key)
        
        self.tools = []
        for t_id in tool_ids:
            if t_id in TOOL_FUNCTIONS:
                self.tools.append(TOOL_FUNCTIONS[t_id])
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=self.tools if self.tools else None,
            system_instruction=role
        )

    def run(self, input_data):
        try:
            # تفعيل استدعاء الدوال التلقائي
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            prompt = f"Input: {input_data}\nPerform your task based on your role."
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error in agent {self.name}: {str(e)}"
