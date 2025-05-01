# core/function_router.py

# Import the map containing the actual executable Python functions
# from your command registry.
# Make sure command_registry.py has a dictionary named executable_functions
try:
    from commands.command_registry import executable_functions
except ImportError:
    print("Error: Could not import executable_functions from commands.command_registry.")
    print("Please ensure commands/command_registry.py exists and contains 'executable_functions'.")
    # Depending on how you want to handle this in your application,
    # you might raise an exception or exit. For robustness, let's define
    # an empty map if import fails, though this means no functions can be called.
    executable_functions = {}
    # In a real app, you'd likely want to fail hard here during startup.


def route_function_call(function_call):
    """
    Routes the function call from the Gemini model to the respective
    executable Python function based on the function name.

    Args:
        function_call: A types.FunctionCall object received from the model.

    Returns:
        The result of the executed function, or an error message string.
    """
    func_name = function_call.name
    # function_call.args is a dictionary of arguments provided by the model
    args = function_call.args
    print(f"Attempting to route and execute function: {func_name} with args: {args}")

    # Check if the function name exists in our map of executable functions
    if func_name in executable_functions:
        try:
            # Get the actual Python function from the map
            func_to_run = executable_functions[func_name]

            # Call the function with its respective arguments.
            # The '**args' unpacks the dictionary into keyword arguments.
            # Ensure your functions can accept arguments this way.
            result = func_to_run(**args)
            print(f"Function '{func_name}' executed successfully.")
            return result # Return the result of the function execution

        except TypeError as e:
            # This handles cases where the model provided arguments that don't match
            # the expected signature of your Python function.
            print(f"Error: Argument mismatch for function '{func_name}': {e}")
            return f"❌ Error: Incorrect arguments provided for function '{func_name}'. Details: {e}"
        except Exception as e:
            # Catch any other exceptions that occur during the function's execution
            print(f"❌ An error occurred during execution of '{func_name}': {e}")
            return f"❌ Error during execution of function '{func_name}': {e}"
    else:
        # This happens if the model requests a function name that isn't in our registry
        print(f"❌ Error: Model requested unknown function: {func_name}")
        return f"❌ Error: Unknown function requested by model: {func_name}"