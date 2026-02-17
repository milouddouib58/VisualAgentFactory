import math
def web_search(query: str):
    return f"Simulated search result for: {query}. (Graphviz requires binary on Android, might not render)."
def calculator(expression: str):
    try:
        return str(eval(expression, {"__builtins__": {}}, {"math": math}))
    except: return "Error"
TOOL_FUNCTIONS = {"web_search": web_search, "calculator": calculator}