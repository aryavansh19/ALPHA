import os
import json
from google import genai
from google.genai import types
from core.function_router import route_function_call
from google.generativeai.types import Tool, FunctionDeclaration

# Import rich components
from rich.console import Console
from rich.text import Text
# Import rich components
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns # Useful for structured content, though not strictly needed here
from rich import print as rich_print # Alias rich's print for convenience

# --- Initialize rich Console ---
console = Console()

# --- Tool Schemas (assuming these imports work correctly and schemas are dicts) ---
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

def display_welcome_message():
    """Displays a welcoming and informative message for the user."""

    welcome_heading = Text()
    welcome_heading.append("Welcome to your Model", style="bold")
    explanation = (
        "I am an AI assistant designed to help you automate various tasks on your computer "
        "and online, simply by understanding your natural language commands. "
        "Think of me as your personal, highly capable script executor!\n\n"
        "I can manage files and folders, create Python scripts, interact with websites, "
        "and even perform specific web automation tasks."
    )

    examples_title = Text("\nHere are a few examples of what I can do:", style="bold blue")

    examples = [
        Text("📂 Folder & File Management:"),
        Text(""), # Empty line for spacing
        Text("🌐 Web & Automation Tasks:"),
    ]

    how_to_use = Text("\nHow to use:", style="bold green")
    how_to_use.append("\n  - Simply type your command or request at the prompt.", style="default")
    #how_to_use.append("\n  - Type '[red bold]exit[/red bold]' to quit the conversation.", style="default")

    # Combine all parts into a single Text object for the Panel
    panel_content = Text.assemble(
        welcome_heading, "\n\n",
        explanation, "\n\n",
        examples_title, "\n"
    )

    for ex_line in examples:
        panel_content.append(ex_line)
        panel_content.append("\n") # Add newline after each example line

    panel_content.append(how_to_use)

    welcome_panel = Panel(
        panel_content,
        title="[bold blue]🤖 AI Assistant Ready! 🤖[/bold blue]",
        border_style="purple",
        expand=True, # Makes the panel expand to fill available width
        padding=(1, 2)
    )

    console.print(welcome_panel)


try:

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")
    #chat = client.chats.create(model="gemini-2.0-flash-live-001")
    console.print("[bold green] Initialization successfull![/bold green]")

except Exception as e:
    console.print(f"[bold red]Error initializing model during the main loop:[/bold red] [red]{e}[/red]")
    # Exit or handle this error more gracefully in a real app
    exit(1) # Exit if API fails to initialize

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

    console.print("\n[bold blue]Assistant:[/bold blue] [green]Website created successfully.[/green] Do you want to open it now? ([cyan]yes/no[/cyan])")
    user_wants_to_open = console.input("[yellow]Your choice:[/yellow] ").strip().lower() # Use console.input for styled prompt

    if user_wants_to_open == 'yes' or user_wants_to_open == 'y':
        console.print("[bold blue]Assistant:[/bold blue] [dim]Okay, attempting to open the website...[/dim]")
        open_website_call_object = types.FunctionCall(
            name='open_website',
            args={'index_html_path': created_website_path}
        )
        function_result = route_function_call(open_website_call_object) # Changed variable name to avoid confusion
        console.print(f"[dim purple]Function execution result (open_website):[/dim purple] [purple]{function_result}[/purple]")
        return types.Part.from_function_result(
            name='open_website',
            response=json.dumps(function_result) # Use function_result here
        )
    else:
        console.print("[bold blue]Assistant:[/bold blue] [yellow]Okay, I won't open the website for now.[/yellow]")
        return None

display_welcome_message()

while True:
    user_prompt = console.input("[bold cyan]Enter your prompt (type '[red]exit[/red]' to quit):[/bold cyan] ") # Use console.input for styled prompt
    if user_prompt.lower() == 'exit':
        break

    try:

        response = chat.send_message(user_prompt, config=config)

        if response.candidates and response.candidates[0].content.parts:
            first_part = response.candidates[0].content.parts[0]
            if first_part.text:
                console.print(f"[bold green]Assistant:[/bold green] {first_part.text}")
            elif first_part.function_call:
                tool_call = first_part.function_call
                tool_name = tool_call.name
                console.print(f"[bold magenta]Model called function:[/bold magenta] [cyan]{tool_name}[/cyan] with args: [dim]{tool_call.args}[/dim]")

                # Route the function call to the appropriate Python function
                function_result = route_function_call(tool_call)

                # Handle the result from the function execution
                console.print(f"[dim purple]Function execution result:[/dim purple] [purple]{function_result}[/purple]")

                console.print("[dim]Sending function result back to Model for confirmation...[/dim]")
                response = chat.send_message("Function Result: " + str(function_result) + "So draft small confirming message")
                if response.text:
                    console.print(f"[bold green]Assistant ([cyan]{tool_name}[/cyan]):[/bold green] {response.text}")

            else:
                console.print("[bold red]Error:[/bold red] Model response contained neither text nor a function call.")
        else:
            console.print("[bold red]Error:[/bold red] No response content received from the model.")

    except Exception as e:
        console.print(f"[bold red]An error occurred during the API call:[/bold red] [red]{e}[/red]")
        # You might want to print a traceback here for more detailed debugging:
        # console.print_exception(show_locals=True)

console.print("\n[bold yellow]Exiting conversation.[/bold yellow]")