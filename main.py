import os
from google import genai
from google.genai import types
from commands.folder.create import create_folder_schema_dict, create_folder

# --- Gemini API Configuration ---
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error initializing Gemini API client: {e}")
    exit()

# --- Tool Configuration ---
tools = types.Tool(function_declarations=[create_folder_schema_dict])
config = types.GenerateContentConfig(tools=[tools])

# --- Conversation Loop ---
contents = []
while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    # --- Add user prompt to history ---
    contents.append(types.Content(role="user", parts=[types.Part(text=user_prompt)]))

    try:
        # --- Send request to Gemini ---
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=config,
            contents=contents
        )

        # --- Process the response ---
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if hasattr(first_part, 'function_call') and first_part.function_call:
                tool_call = first_part.function_call
                print(f"Model called function: {tool_call.name} with args: {tool_call.args}")
                if tool_call.name == "create_folder":
                    try:
                        result = create_folder(**tool_call.args)
                        print(f"Function execution result: {result}")

                        # --- Append function call and result to history ---
                        contents.append(types.Content(role="model", parts=[types.Part(function_call=tool_call)]))
                        function_response_part = types.Part.from_function_response(
                            name=tool_call.name,
                            response={"result": result},
                        )
                        contents.append(types.Content(role="tool", parts=[function_response_part]))

                        # --- Send follow-up request ---
                        follow_up_response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            config=config,
                            contents=contents,
                        )

                        # --- Print final response ---
                        if follow_up_response.candidates and follow_up_response.candidates[0].content and follow_up_response.candidates[0].content.parts:
                            final_text_part = next((part.text for part in follow_up_response.candidates[0].content.parts if part.text), None)
                            if final_text_part:
                                print("\nFinal Model Response:")
                                print(final_text_part)
                            else:
                                print("\nModel finished successfully but did not return a text response.")
                        else:
                            print("\nNo final response received after tool execution.")

                    except Exception as e:
                        print(f"Error executing function or follow-up API call: {e}")
                        # Consider adding an error message to history for the model
                else:
                    print(f"Model called unexpected function: {tool_call.name}")
                    # Consider how to handle unexpected function calls in the conversation history
                    contents.append(types.Content(role="model", parts=[types.Part(function_call=tool_call)])) # Add the unexpected call to history
            elif hasattr(first_part, 'text') and first_part.text:
                print("\nModel responded with text:")
                print(first_part.text)
                # Append the model's text response to history
                contents.append(types.Content(role="model", parts=[types.Part(text=first_part.text)]))
            else:
                print("\nModel response did not contain text or a function call.")
        else:
            print("\nNo response content received from the model.")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        # Consider how to inform the user or the model about the error in the conversation history

print("\nExiting conversation.")