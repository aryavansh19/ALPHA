
import os
from google.genai import types


create_folder_schema_dict = {
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


def create_folder(folder_name: str, location: str):
    print(f"We have created new Folder at {location} with name {folder_name}")
    return "Done"
