import requests
import json

class AtomicAgent:
    def __init__(self, api_key, name, role, model_name, tool_ids):
        self.api_key = api_key
        self.name = name
        self.role = role
        # تنظيف اسم الموديل للتأكد من توافقه
        self.model_name = model_name.strip()
        # إذا كان الاسم لا يبدأ بكلمة models/، نضيفها (بعض النسخ تتطلبها)
        # لكن في النسخة الحالية requests تعمل غالباً بدون البادئة إذا كانت صحيحة
        # سنعتمد الاسم كما يأتي من القائمة المختارة
        self.tool_ids = tool_ids

    def run(self, input_data):
        if not self.api_key:
            return "Error: API Key is missing."

        # بناء الرابط باستخدام الموديل المختار
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
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
                    return f"Error: Unexpected response format. {result}"
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Connection Error: {str(e)}"


