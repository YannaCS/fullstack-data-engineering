import os
from getpass import getpass
from openai import OpenAI
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API Key

# Check if already set in environment
api_key = os.environ.get("OPENAI_API_KEY", "")

if not api_key:
    # Prompt for API key (input will be hidden)
    api_key = getpass("Enter your OpenAI API Key: ")
    os.environ["OPENAI_API_KEY"] = api_key

if api_key:
    print(f"[OK] API Key set")
else:
    print("[ERROR] No API key provided!")

client = OpenAI()

# =============================================================================
# STEP 1: Define the actual tool function
# =============================================================================
def get_weather(latitude, longitude):
    """Calls weather API and returns current temperature"""
    response = requests.get(
        f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m'
    )
    data = response.json()
    return data['current']['temperature_2m']

# =============================================================================
# STEP 2: Define tool schema for the model (CORRECTED FORMAT)
# =============================================================================
tools = [{
    "type": "function",
    "function": {  # <-- Need this wrapper!
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

# =============================================================================
# STEP 3: Send initial request to model
# =============================================================================
input_messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=input_messages,
    tools=tools,
)

# =============================================================================
# STEP 4: Check if model wants to call a tool
# =============================================================================
assistant_message = response.choices[0].message

print("=== Model Response ===")
print(f"Content: {assistant_message.content}")
print(f"Tool Calls: {assistant_message.tool_calls}")

# If model wants to call a tool
if assistant_message.tool_calls:
    
    # =============================================================================
    # STEP 5: Execute the tool function
    # =============================================================================
    tool_call = assistant_message.tool_calls[0]
    
    print(f"\n=== Tool Call ===")
    print(f"Function: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
    
    # Parse arguments and call the actual function
    args = json.loads(tool_call.function.arguments)
    
    # Execute the tool
    result = get_weather(
        latitude=args["latitude"],
        longitude=args["longitude"]
    )
    
    print(f"Result: {result}°C")
    
    # =============================================================================
    # STEP 6: Send tool result back to model
    # =============================================================================
    input_messages.append(assistant_message)
    
    input_messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"temperature": result, "unit": "celsius"})
    })
    
    # =============================================================================
    # STEP 7: Get final response from model
    # =============================================================================
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=input_messages,
        tools=tools,
    )
    
    final_answer = final_response.choices[0].message.content
    
    print(f"\n=== Final Answer ===")
    print(final_answer)

else:
    print(f"\nDirect Answer: {assistant_message.content}")