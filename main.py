import os
import time
from google import genai
from google.genai import types
from core.function_router import route_function_call
from google.generativeai.types import Tool, FunctionDeclaration
from commands.folder.create import create_folder_schema_dict, create_folder
from commands.folder.delete import delete_folders_schema_dict, delete_folders
from commands.folder.move import move_folders_schema_dict, move_folders
from commands.folder.rename import rename_folders_schema_dict, rename_folders
from commands.files.create_python_file import create_python_file_schema_dict, create_python_file

#--- Gemini API Configurations ---
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")
    #chat = client.chats.create(model="gemini-2.0-flash-live-001")

except Exception as e:
    print(f"Error initializing Gemini API or during the main loop: {e}")

# --- Tool Configuration ---
tools = [types.Tool(function_declarations=
                    [create_folder_schema_dict,
                     delete_folders_schema_dict,
                     move_folders_schema_dict,
                     rename_folders_schema_dict,
                     create_python_file_schema_dict,]
                    )]
#config = types.GenerateContentConfig(tools=[tools])
config = {
    "tools": tools,
    "automatic_function_calling": {"disable": True}
}

def execute_function_call(tool_call, chat):
    """Execute a single function call and handle its response"""
    tool_name = tool_call.name
    print(f"\nExecuting function: {tool_name} with args: {tool_call.args}")
    
    # Route the function call to the appropriate Python function
    function_result = route_function_call(tool_call)
    
    # Handle the result from the function execution
    print(f"Function execution result: {function_result}")
    
    # Send result back to model and get confirmation
    response = chat.send_message("Function Result: " + str(function_result) + ". Please continue with next step if any, or provide a confirmation message.")
    return response

while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    try:
        response = chat.send_message(user_prompt, config=config)
        
        while response.candidates and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            
            if first_part.text:
                print(first_part.text)
                break  # No more function calls to process
                
            elif first_part.function_call:
                # Execute the function call
                response = execute_function_call(first_part.function_call, chat)
                
                # Add a small delay between sequential operations
                time.sleep(1)
                
            else:
                print("Model response contained neither text nor a function call.")
                break

    except Exception as e:
        print(f"An error occurred during the API call: {e}")

print("\nExiting conversation.")
