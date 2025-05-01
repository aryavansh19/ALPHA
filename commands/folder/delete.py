import os
import shutil
from google.genai import types

# Function schema for Gemini
delete_folder_schema_dict = {
    "name": "delete_folder",
    "description": "Deletes an existing folder in a known user directory like Desktop or Documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Name of the folder to delete."
            },
            "location": {
                "type": "string",
                "description": "Location where the folder is (e.g., 'Desktop', 'Documents')."
            }
        },
        "required": ["folder_name", "location"]
    }
}

delete_folder_tool_schema = types.FunctionDeclaration(**delete_folder_schema_dict)

# Actual delete folder logic
def delete_folder(folder_name: str, location: str) -> str:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}

    if location not in valid_locations:
        return f"❌ Invalid location '{location}'. Choose from: {', '.join(valid_locations)}"

    folder_path = os.path.join(base_user_path, location, folder_name)

    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # Remove folder and its contents
            return f"✅ Folder '{folder_name}' deleted from {location}."
        else:
            return f"❌ Folder '{folder_name}' does not exist at {location}."
    except Exception as e:
        return f"❌ Failed to delete folder: {e}"
