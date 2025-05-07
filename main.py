import os
from google import genai
from commands.folder.create import create_folder_schema_dict, create_folder
from commands.folder.delete import delete_folders_schema_dict, delete_folders
from commands.folder.move import move_folders_schema_dict, move_folders
from commands.folder.rename import rename_folders_schema_dict, rename_folders
from core.function_router import route_function_call
from google.generativeai.types import Tool, FunctionDeclaration
from google.genai import types

#--- Gemini API Configurations ---
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")

except Exception as e:
    print(f"Error initializing Gemini API or during the main loop: {e}")

# --- Tool Configuration ---
tools = [types.Tool(function_declarations=[create_folder_schema_dict, delete_folders_schema_dict, move_folders_schema_dict, rename_folders_schema_dict])]
#config = types.GenerateContentConfig(tools=[tools])
config = {
    "tools": tools,
    "automatic_function_calling": {"disable": True}
    # Force the model to call 'any' function, instead of chatting.
}

while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    try:
        response = chat.send_message(user_prompt, config=config)

        if response.candidates and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if first_part.text:
                #print("Model Response (Text):")
                print(first_part.text)
            elif first_part.function_call:
                tool_call = first_part.function_call
                tool_name = tool_call.name
                print(f"Model called function: {tool_name} with args: {tool_call.args}")

                # Route the function call to the appropriate Python function
                function_result = route_function_call(tool_call)

                # Handle the result from the function execution
                print(f"Function execution result: {function_result}")

                response = chat.send_message("Function Result: " + str(function_result) + "So draft small confirming message")
                if response.text:
                    print(f"Model response after {tool_name}: {response.text}")

            else:
                print("Model response contained neither text nor a function call.")
        else:
            print("No response content received from the model.")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")

print("\nExiting conversation.")
