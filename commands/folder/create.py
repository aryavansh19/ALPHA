# commands/folder/create.py
import os
from google.genai import types # Import the types module

# The schema information as a dictionary (as you already have it)
create_folder_schema_dict = { # Renamed for clarity
    "name": "create_folder",
    "description": "Creates a folder inside a known user directory like Desktop or Documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Name of the folder to create."
            },
            "location": {
                "type": "string",
                "description": "Target location under the user directory (e.g., 'Desktop', 'Documents')."
            }
        },
        "required": ["folder_name", "location"]
    }
}

# Convert the dictionary into a types.FunctionDeclaration object
# This is the object the Gemini API needs
create_folder_tool_schema = types.FunctionDeclaration(**create_folder_schema_dict)


# Actual folder creation logic (your existing function)
def create_folder(folder_name: str, location: str) -> str:
    """Creates a new folder at the specified path."""
    # Using your base path and valid locations
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}

    if location not in valid_locations:
        # This return string will be the tool output
        return f"❌ Invalid location '{location}'. Choose from: {', '.join(valid_locations)}"

    target_path = os.path.join(base_user_path, location, folder_name)

    try:
        os.makedirs(target_path, exist_ok=True)
        # This return string will be the tool output
        return f"✅ Folder '{folder_name}' created at {target_path}."
    except Exception as e:
        # This return string will be the tool output
        return f"❌ Failed to create folder: {e}"

# You should do similar steps in your delete.py, rename.py, and move.py
# - Define the schema dictionary
# - Convert it to a types.FunctionDeclaration object (e.g., delete_folder_tool_schema)
# - Keep the executable function (e.g., delete_folder)