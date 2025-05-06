import os
from google import genai
from commands.folder.create import create_folder_schema_dict, create_folder
from google.generativeai.types import Tool, FunctionDeclaration
from google.genai import types

#--- Gemini API Configuration ---
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")

except Exception as e:
    print(f"Error initializing Gemini API or during the main loop: {e}")

# --- Tool Configuration ---
tools = types.Tool(function_declarations=[create_folder_schema_dict])
config = types.GenerateContentConfig(tools=[tools])

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
                #print("Model Called Function:")
                print(first_part.function_call)
                tool_call = first_part.function_call
                if tool_call.name == "create_folder":
                    try:
                        location = tool_call.args.get("location")
                        folder_names = tool_call.args.get("folder_names")

                        if location and folder_names:
                            results = create_folder(location=location, folder_names=folder_names)
                            print(f"Function execution successful. Results: {results}")
                            #  Consider sending results back to the model
                        else:
                            print("Error: Missing 'location' or 'folder_names' in function arguments.")
                    except Exception as e:
                        print(f"Error executing function: {e}")
                else:
                    print(f"Unknown function called: {tool_call.name}")

            else:
                print("Model response contained neither text nor a function call.")
        else:
            print("No response content received from the model.")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")

print("\nExiting conversation.")
