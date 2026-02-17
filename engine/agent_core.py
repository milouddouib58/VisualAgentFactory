import requests
import json

class AtomicAgent:
    def __init__(self, api_key, name, role, model_name, tool_ids):
        self.api_key = api_key
        self.name = name
        self.role = role
        self.model_name = model_name.strip()
        self.tool_ids = tool_ids

    def run(self, input_data):
        if not self.api_key:
            return "Error: API Key is missing."

        # --- مسار 1: إذا كان الموديل من شركة Mistral ---
        if "mistral" in self.model_name or "mixtral" in self.model_name:
            return self._run_mistral(input_data)
        
        # --- مسار 2: الافتراضي (Google Gemini) ---
        else:
            return self._run_gemini(input_data)

    # دالة خاصة بـ Mistral
    def _run_mistral(self, input_data):
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.role},
                {"role": "user", "content": input_data}
            ],
            "temperature": 0.7
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Mistral Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Connection Error (Mistral): {str(e)}"

    # دالة خاصة بـ Google Gemini
    def _run_gemini(self, input_data):
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
                    return "Error parsing Google response."
            else:
                return f"Google Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Connection Error (Google): {str(e)}"



