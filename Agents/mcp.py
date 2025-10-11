import json
from tools import add_numbers

Tools = {
    "add_numbers": add_numbers
}

def handle_request(request_json: str) -> str:
    request = json.loads(request_json)
    tool_name = request.get("tool")
    params = request.get("parameters", {})
    request_id = request.get("request_id", "0")
    
    if tool_name not in TOOLS:
        return json.dumps({
            "request_id": request_id,
            "error": f"Unknown tool {tool_name}"
        })
        
    result = TOOLS[tool_name](**params)
    return json.dumps({
        "request_id": request_id,
        "result": result
    })