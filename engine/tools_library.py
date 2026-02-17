import math

def web_search(query: str):
    """
    Simulates a web search for the agent.
    """
    print(f"Debug: Searching for {query}")
    # محاكاة نتائج بحث لعدم الحاجة لمفتاح Serper حالياً
    mock_knowledge = {
        "weather": "The weather is currently sunny, 25 degrees Celsius.",
        "ai": "Artificial Intelligence is evolving rapidly with LLMs like Gemini.",
        "python": "Python is a versatile programming language popular in Data Science.",
        "agent": "Agents are autonomous systems powered by LLMs."
    }
    
    for key, val in mock_knowledge.items():
        if key in query.lower():
            return val
            
    return f"Found generic information regarding '{query}'. It is a very interesting topic."

def calculator(expression: str):
    """
    Safely evaluates a mathematical expression.
    """
    try:
        allowed_names = {"abs": abs, "round": round, "math": math}
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                return f"Error: Forbidden function '{name}'"
        return str(eval(code, {"__builtins__": {}}, allowed_names))
    except Exception as e:
        return f"Calc Error: {str(e)}"

# سجل الأدوات
TOOL_FUNCTIONS = {
    "web_search": web_search,
    "calculator": calculator
}
