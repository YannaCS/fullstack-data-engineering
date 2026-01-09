import anthropic
import os
from getpass import getpass
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Set your Anthropic API Key

# Check if already set in environment
api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if not api_key:
    # Prompt for API key (input will be hidden)
    api_key = getpass("Enter your Anthropic API Key: ")
    os.environ["ANTHROPIC_API_KEY"] = api_key

if api_key:
    print(f"[OK] API Key set")
else:
    print("[ERROR] No API key provided!")

client = anthropic.Anthropic()

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
# STEP 2: Define tool schema for the model (Anthropic format)
# =============================================================================
tools = [
    {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude coordinate"
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude coordinate"
                }
            },
            "required": ["latitude", "longitude"]
        }
    }
]

# =============================================================================
# STEP 3: Send initial request to model
# =============================================================================
messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

# =============================================================================
# STEP 4: Check if model wants to call a tool
# =============================================================================
print("=== Model Response ===")
print(f"Stop Reason: {response.stop_reason}")
print(f"Content: {response.content}")

# If model wants to call a tool (stop_reason == "tool_use")
if response.stop_reason == "tool_use":
    
    # =============================================================================
    # STEP 5: Extract tool call and execute
    # =============================================================================
    # Find the tool_use block in content
    tool_use_block = None
    text_block = None
    
    for block in response.content:
        if block.type == "tool_use":
            tool_use_block = block
        elif block.type == "text":
            text_block = block
    
    print(f"\n=== Tool Call ===")
    print(f"Tool ID: {tool_use_block.id}")
    print(f"Function: {tool_use_block.name}")
    print(f"Arguments: {tool_use_block.input}")
    
    if text_block:
        print(f"Model Thinking: {text_block.text.encode('utf-8').decode('utf-8')}")
    
    # Execute the tool
    result = get_weather(
        latitude=tool_use_block.input["latitude"],
        longitude=tool_use_block.input["longitude"]
    )
    
    print(f"Result: {result}°C")
    
    # =============================================================================
    # STEP 6: Send tool result back to model
    # =============================================================================
    # Add assistant's response to messages
    messages.append({
        "role": "assistant",
        "content": response.content
    })
    
    # Add tool result
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": json.dumps({"temperature": result, "unit": "celsius"})
            }
        ]
    })
    
    # =============================================================================
    # STEP 7: Get final response from model
    # =============================================================================
    final_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )
    
    # Extract text from final response
    final_answer = ""
    for block in final_response.content:
        if hasattr(block, "text"):
            final_answer += block.text
    
    print(f"\n=== Final Answer ===")
    print(final_answer)

else:
    # Model answered directly without tool
    print(f"\nDirect Answer: {response.content[0].text}")