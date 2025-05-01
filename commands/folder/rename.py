import os
from google.genai import types
# Function schema for Gemini
rename_folder_schema_dict = {
    "name": "rename_folder",
    "description": "Renames an existing folder in a known user directory like Desktop or Documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "old_folder_name": {
                "type": "string",
                "description": "Current name of the folder."
            },
            "new_folder_name": {
                "type": "string",
                "description": "New name for the folder."
            },
            "location": {
                "type": "string",
                "description": "Location where the folder is (e.g., 'Desktop', 'Documents')."
            }
        },
        "required": ["old_folder_name", "new_folder_name", "location"]
    }
}

rename_folder_tool_schema = types.FunctionDeclaration(**rename_folder_schema_dict)

# Actual rename folder logic
def rename_folder(old_folder_name: str, new_folder_name: str, location: str) -> str:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}

    if location not in valid_locations:
        return f"❌ Invalid location '{location}'. Choose from: {', '.join(valid_locations)}"

    old_folder_path = os.path.join(base_user_path, location, old_folder_name)
    new_folder_path = os.path.join(base_user_path, location, new_folder_name)

    try:
        os.rename(old_folder_path, new_folder_path)
        return f"✅ Folder renamed from '{old_folder_name}' to '{new_folder_name}' at {location}."
    except FileNotFoundError:
        return f"❌ Folder '{old_folder_name}' not found at {location}."
    except Exception as e:
        return f"❌ Failed to rename folder: {e}"
