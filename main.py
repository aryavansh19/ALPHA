import os
from google import genai
from commands.folder.create import create_folder_schema_dict, create_folder
from google.generativeai.types import Tool, FunctionDeclaration
from google.genai import types

# --- Gemini API Configuration ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Conversation Loop using ChatSession ---
tools = types.Tool(function_declarations=[create_folder_schema_dict])
config = types.GenerateContentConfig(tools=[tools])


while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    contents = [
        types.Content(
            role="user", parts=[types.Part(text=user_prompt)]
        )
    ]

    response = client.models.generate_content(
        model="gemini-2.0-flash", config=config, contents=contents
    )
    print(response.candidates[0].content.parts[0].function_call)


    tool_call = response.candidates[0].content.parts[0].function_call

    if tool_call.name == "create_folder":
        result = create_folder(**tool_call.args)

    function_response_part = types.Part.from_function_response(
        name=tool_call.name,
        response={"result": result},
    )

    # Append function call and result of the function execution to contents
    contents.append(types.Content(role="model", parts=[
        types.Part(function_call=tool_call)]))  # Append the model's function call message
    contents.append(types.Content(role="user", parts=[function_response_part]))  # Append the function response

    final_response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=config,
        contents=contents,
    )

    print(final_response.text)

print("\nExiting conversation.")

