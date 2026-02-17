import requests
import json

class AtomicAgent:
    def __init__(self, api_key, name, role, model_name, tool_ids):
        self.api_key = api_key
        self.name = name
        self.role = role
        # تصحيح اسم الموديل ليتوافق مع API
        self.model_name = "gemini-1.5-flash" if "flash" in model_name else "gemini-pro"
        self.tool_ids = tool_ids

    def run(self, input_data):
        if not self.api_key:
            return "Error: API Key is missing."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        # صياغة الطلب
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"System Role: {self.role}\n\nTask: {input_data}"
                }]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return result['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    return "Error: Unexpected response format from Gemini."
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Connection Error: {str(e)}"

