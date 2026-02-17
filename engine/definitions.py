import streamlit as st

# القائمة المحدثة لتشمل جوجل وميسترال
AVAILABLE_MODELS = [
    "gemini-1.5-flash",    # جوجل (سريع ومجاني)
    "gemini-2.0-flash",    # جوجل (جديد)
    "open-mistral-7b",     # ميسترال (مجاني وسريع)
    "open-mixtral-8x7b",   # ميسترال (ذكي جداً وقوي)
    "mistral-small-latest" # ميسترال (خفيف)
]

AVAILABLE_TOOLS = [
    {
        "id": "web_search",
        "name": "Web Search (Simulated)",
        "description": "Simulates searching the web for information."
    },
    {
        "id": "calculator",
        "name": "Calculator",
        "description": "Performs basic arithmetic calculations."
    }
]
