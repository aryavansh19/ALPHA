import os
from google import genai
from google.generativeai.types import FunctionDeclaration

# Function definition
def get_current_weather(location: str, unit: str = "celsius"):
    """Gets the current weather in a given location."""
    weather_data = {
        "location": location,
        "temperature": 25,
        "unit": unit,
        "description": "Sunny",
    }
    return weather_data

# Function schema
get_current_weather_schema = {
    "name": "get_current_weather",
    "description": "Gets the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. 'San Francisco, CA'",
            },
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
    },
}

# Initialize Gemini client
genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # or "gemini-1.5-pro"
    tools=[FunctionDeclaration(**get_current_weather_schema)]
)

chat = model.start_chat()

# Conversation loop
while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    response = chat.send_message(user_prompt)

    for part in response.parts:
        if hasattr(part, 'function_call') and part.function_call:
            tool_call = part.function_call
            print(f"Model called function: {tool_call.name} with args: {tool_call.args}")

            if tool_call.name == "get_current_weather":
                try:
                    weather_result = get_current_weather(**tool_call.args)
                    print(f"Function execution result: {weather_result}")

                    tool_response = chat.send_tool_output(
                        name=tool_call.name,
                        content=weather_result
                    )

                    print("\nModel Response after tool output:")
                    print(tool_response.text)

                except Exception as e:
                    print(f"Error executing function: {e}")
                    error_response = chat.send_tool_output(
                        name=tool_call.name,
                        content={"error": str(e)}
                    )
                    print("\nModel Response after function error:")
                    print(error_response.text)
        else:
            print("\nModel Response:")
            print(part.text)

print("\nExiting conversation.")
