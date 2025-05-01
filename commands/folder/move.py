import os
import shutil
from google.genai import types

# Function schema for Gemini
move_folder_schema_dict = {
    "name": "move_folder",
    "description": "Moves a folder from one location to another within known user directories like Desktop or Documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Name of the folder to move."
            },
            "source_location": {
                "type": "string",
                "description": "Current location where the folder is (e.g., 'Desktop', 'Documents')."
            },
            "target_location": {
                "type": "string",
                "description": "Destination location (e.g., 'Desktop', 'Documents')."
            }
        },
        "required": ["folder_name", "source_location", "target_location"]
    }
}

move_folder_tool_schema = types.FunctionDeclaration(**move_folder_schema_dict)

# Actual move folder logic
def move_folder(folder_name: str, source_location: str, target_location: str) -> str:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}

    if source_location not in valid_locations or target_location not in valid_locations:
        return f"❌ Invalid location(s). Choose from: {', '.join(valid_locations)}"

    source_folder_path = os.path.join(base_user_path, source_location, folder_name)
    target_folder_path = os.path.join(base_user_path, target_location, folder_name)

    try:
        if os.path.exists(source_folder_path):
            shutil.move(source_folder_path, target_folder_path)
            return f"✅ Folder '{folder_name}' moved from {source_location} to {target_location}."
        else:
            return f"❌ Folder '{folder_name}' not found at {source_location}."
    except Exception as e:
        return f"❌ Failed to move folder: {e}"
