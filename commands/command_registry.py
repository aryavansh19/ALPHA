# commands/command_registry.py

# --- Import FunctionDeclaration Schemas (the types.FunctionDeclaration objects) ---
from commands.folder.create import create_folder_tool_schema
from commands.folder.delete import delete_folder_tool_schema # Assuming you defined this in delete.py
from commands.folder.rename import rename_folder_tool_schema # Assuming you defined this in rename.py
from commands.folder.move import move_folder_tool_schema   # Assuming you defined this in move.py
# Import schemas for any other command modules

# --- Import Executable Functions (the actual Python code) ---
from commands.folder.create import create_folder
from commands.folder.delete import delete_folder
from commands.folder.rename import rename_folder
from commands.folder.move import move_folder
# Import executable functions for any other command modules


# --- Mappings ---

# This dictionary maps function names (used by the model) to their FunctionDeclaration schemas
# This is what you will use to configure the Gemini API tools in main.py
function_schemas = {
    "create_folder": create_folder_tool_schema,
    "delete_folder": delete_folder_tool_schema,
    "rename_folder": rename_folder_tool_schema,
    "move_folder": move_folder_tool_schema,
    # Add other function_name: schema_variable mappings
}

# This dictionary maps function names (used by the model) to their executable Python functions
# This is what your route_function_call will use to find and run the correct code
executable_functions = {
    "create_folder": create_folder,
    "delete_folder": delete_folder,
    "rename_folder": rename_folder,
    "move_folder": move_folder,
    # Add other function_name: executable_function mappings
}

# ... (Your route_function_call logic in core/function_router.py should use executable_functions)