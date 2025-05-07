from commands.folder.create import create_folder
from commands.folder.delete import delete_folders
from commands.folder.move import move_folders
from commands.folder.rename import rename_folders

executable_functions = {
    "create_folder": create_folder,
    "delete_folders": delete_folders,
    "move_folders": move_folders,
    "rename_folders": rename_folders,
}
