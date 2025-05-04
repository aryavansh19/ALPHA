import os
from google import genai
from commands.folder.create import create_folder_schema_dict, create_folder
from google.generativeai.types import Tool, FunctionDeclaration
from google.genai import types

# --- Gemini API Configuration ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat = client.chats.create(model="gemini-2.0-flash")

# --- Conversation Loop using ChatSession ---
tools = types.Tool(function_declarations=[create_folder_schema_dict])
config = types.GenerateContentConfig(tools=[tools])


# response = chat.send_message("I have 2 dogs in my house.")
# print(response.text)

while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    contents = [
        types.Content(
            role="user", parts=[types.Part(text=user_prompt)]
        )
    ]

    response = chat.send_message(user_prompt, config=config)
    print(response.candidates[0].content.parts[0].function_call)

    # response = client.models.generate_content(
    #     model="gemini-2.0-flash", contents=contents
    # )
    #
    # print(response.text)


print("\nExiting conversation.")

