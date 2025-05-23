import os
import json
from google import genai
from google.genai import types
from core.function_router import route_function_call
from google.generativeai.types import Tool, FunctionDeclaration
from commands.folder.create import create_folder_schema_dict, create_folder
from commands.folder.delete import delete_folders_schema_dict, delete_folders
from commands.folder.move import move_folders_schema_dict, move_folders
from commands.folder.rename import rename_folders_schema_dict, rename_folders
from commands.files.create_python_file import create_python_file_schema_dict, create_python_file
from commands.website.create_website import create_website_schema_dict, create_website
from commands.website.open_website import open_website_schema_dict, open_website
from commands.webautomation.youtube_Automation import open_youtube_trending_schema_dict
from commands.webautomation.web_scrapper import scrape_website_content_schema_dict
from commands.webautomation.gehu_Automation import open_gehu_btech_notice_and_return_content_schema_dict
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os


class CommandParser:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "command_model")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = T5Tokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
        self.model.to(self.device)
        self.model.eval()

    def parse_command(self, text):
        # Tokenize input
        inputs = self.tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate output
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=128,
                num_beams=4,
                early_stopping=True
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text


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
                     create_python_file_schema_dict,
                     create_website_schema_dict,
                     open_website_schema_dict,
                     open_youtube_trending_schema_dict,
                     scrape_website_content_schema_dict,
                     open_gehu_btech_notice_and_return_content_schema_dict,]
                    )]
#config = types.GenerateContentConfig(tools=[tools])
config = {
    "tools": tools,
    "automatic_function_calling": {"disable": True}
}

def handle_website_creation_follow_up(created_website_path: str) -> types.Part:
    """
    Asks the user if they want to open the newly created website
    and executes the open_website command if confirmed.
    Returns the result of the open_website call as a types.Part for Gemini.
    """
    print("\nAssistant: Website created successfully. Do you want to open it now? (yes/no)")
    user_wants_to_open = input("Your choice: ").strip().lower()

    if user_wants_to_open == 'yes' or user_wants_to_open == 'y':
        print("Assistant: Okay, attempting to open the website...")
        open_website_call_object = types.FunctionCall(
            name='open_website',
            args={'index_html_path': created_website_path}
        )
        open_website_result = route_function_call(open_website_call_object)
        print(f"Function execution result (open_website): {open_website_result}")
        return types.Part.from_function_result(
            name='open_website',
            response=json.dumps(open_website_result)
        )
    else:
        print("Assistant: Okay, I won't open the website for now.")
        # Return an empty part or a message indicating no action for Gemini if needed
        # For simplicity, if not opened, we don't send a separate Part for 'open_website'
        return None


while True:
    user_prompt = input("Enter your prompt (type 'exit' to quit): ")
    if user_prompt.lower() == 'exit':
        break

    try:
        response = chat.send_message(user_prompt, config=config)

        if response.candidates and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if first_part.text:
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
