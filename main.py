import os
from google import genai
from google.genai import types
import sys  # Import sys for exiting

# Assuming core.function_router and commands are available based on your project structure
# Make sure these modules and functions exist and are correctly implemented
try:
    from core.function_router import route_function_call
except ImportError:
    print("Error: Could not import route_function_call from core.function_router.")
    print("Please ensure core/function_router.py exists and contains the route_function_call function.")
    sys.exit(1)

try:
    from commands import command_registry  # Assuming command_registry is directly in the commands directory
except ImportError:
    print("Error: Could not import command_registry from commands.")
    print("Please ensure commands/command_registry.py exists.")
    sys.exit(1)

# --- Gemini API Configuration ---

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Ensure command_registry.function_schemas exists and contains FunctionDeclaration objects
    if not hasattr(command_registry, 'function_schemas') or not isinstance(command_registry.function_schemas, dict):
        print("Error: command_registry.py must contain a dictionary named 'function_schemas'.")
        sys.exit(1)

    # Get the list of FunctionDeclaration objects from command_registry.function_schemas
    # This resolves the pydantic validation error
    tools = types.Tool(function_declarations=list(command_registry.function_schemas.values()))
    config = types.GenerateContentConfig(tools=[tools])

except Exception as e:
    print(f"Error during Gemini API configuration: {e}")
    sys.exit(1)

# --- Conversation Loop ---
# Initialize an empty list to store the conversation history
# Each element will be a types.Content object representing a turn
conversation_history = []

print("🤖 ALPHA is running. Type 'quit' to exit.")

while True:
    try:
        # Get user input
        user_input = input("You: ")

        # Check for exit command
        if user_input.lower() == 'quit':
            print("Exiting chat.")
            break

        # Prevent sending empty input to the model
        if not user_input.strip():
            continue

        # Add the user's input to the conversation history with the 'user' role
        conversation_history.append(types.Content(role='user', parts=[types.Part(text=user_input)]))

        # --- Call the model with the conversation history ---
        # Pass the entire history so the model remembers previous turns
        response = client.models.generate_content(
            model="gemini-1.5-pro-latest",
            contents=conversation_history,
            config=config  # Pass the tools configuration
        )

        # --- Process the model's response ---

        # Check if the response contains candidates (model output)
        if not response.candidates:
            print("Model: No response generated.")
            # Optionally, remove the last user turn if the model produced no output
            # conversation_history.pop()
            continue  # Skip to the next user input

        candidate = response.candidates[0]

        # Check if the response was blocked for safety reasons
        if candidate.finish_reason == 'SAFETY':
            print("Model: Response blocked for safety reasons.")
            # Optionally, remove the last user turn
            # conversation_history.pop()
            # You might want to print safety ratings for debugging:
            # print(f"Safety ratings: {candidate.safety_ratings}")
            continue  # Skip to the next user input

        # Check for other potential finish reasons (optional)
        if candidate.finish_reason and candidate.finish_reason != 'STOP' and candidate.finish_reason != 'TOOL_CODE':
            print(f"Model finished with reason: {candidate.finish_reason}")
            # Handle other reasons like MAX_TOKENS if necessary

        # Check if the model wants to call a function
        if candidate.content.parts and candidate.content.parts[0].function_call:
            function_call = candidate.content.parts[0].function_call
            print(f"Model: Calling function: {function_call.name} with args: {function_call.args}")

            # Add the model's function call to the history
            # This is the model's turn where it decided to call a tool
            # This is crucial for the model to understand the state of the conversation flow
            conversation_history.append(types.Content(role='model', parts=[types.Part(function_call=function_call)]))

            try:
                # Execute the function call using your router
                # route_function_call should take the types.FunctionCall object
                # and use command_registry.executable_functions to run the correct code.
                result = route_function_call(function_call)
                print(f"Tool Output: {result}")

                # Add the function's result back to the conversation history
                # Use the 'tool' role to indicate this is output from a tool
                # This tells the model the outcome of the action it requested
                conversation_history.append(
                    types.Content(
                        role='tool',
                        parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=function_call.name,
                                # The response dictionary structure must match
                                # what your tool function actually returned and
                                # what its FunctionDeclaration expects as output.
                                # Using a simple {'result': ...} is common if the tool returns a string or simple value.
                                response={'result': result}
                            )
                        )]
                    )
                )

                # --- Follow-up Model Call After Tool Execution ---
                # After a tool call and response, make another model call
                # with the *updated* history (including the tool output)
                # so the model can see the tool result and decide on the next action,
                # typically generating a natural language response to the user.
                follow_up_response = client.models.generate_content(
                    model="gemini-1.5-pro-latest",
                    contents=conversation_history,  # History *now* includes tool output
                    config=config  # Keep tools available for potential further calls
                )

                # --- Process the follow-up response ---
                if not follow_up_response.candidates:
                    print("Model: No follow-up response generated after tool execution.")
                    # The tool output is already in history, so we can continue
                    continue

                final_candidate = follow_up_response.candidates[0]

                if final_candidate.finish_reason == 'SAFETY':
                    print("Model: Follow-up response blocked for safety.")
                    # Tool output is in history, but no model follow-up text
                    continue

                # The follow-up response should ideally be text, but handle other cases
                if final_candidate.content.parts and final_candidate.content.parts[0].text:
                    model_response_text = final_candidate.content.parts[0].text
                    print(f"Model: {model_response_text}")
                    # Add the model's text response to the history for the next turn
                    conversation_history.append(
                        types.Content(role='model', parts=[types.Part(text=model_response_text)]))
                else:
                    print("Model: Received non-text content in follow-up response.")
                    # If the model calls another function immediately, handle that
                    # If it's some other format, you might need specific handling
                    # print(final_candidate) # Debugging help

            except Exception as e:
                # Handle errors specifically during function execution or the follow-up call
                print(f"❌ Error during function execution or follow-up call: {e}")
                # Optionally, add an error message to history as a tool response
                # so the model knows the tool failed. Be cautious about revealing
                # too much internal error info to the model or user.
                # conversation_history.append(types.Content(role='tool', parts=[types.Part(function_response=types.FunctionResponse(name=function_call.name, response={'error': f"Execution failed: {e}"}))]))


        # If the model generated a text response directly (not a function call)
        elif candidate.content.parts and candidate.content.parts[0].text:
            model_text = candidate.content.parts[0].text
            print(f"Model: {model_text}")
            # Add the model's text response to the conversation history
            # This is the model's turn providing a direct response
            conversation_history.append(types.Content(role='model', parts=[types.Part(text=model_text)]))

        # Handle cases where the response is not text or a function call (e.g., image response if model supports it)
        else:
            print("Model: Received an unrecognized response format.")
            # Optionally, print the candidate object for debugging
            # print(candidate)

    except Exception as e:
        # Catch any exceptions during the main API call or initial processing
        print(f"\nAn API or processing error occurred: {e}")
        # If an error happens during the API call or processing its immediate result,
        # the last user input wasn't successfully processed. Removing it from history
        # can help prevent confusing the model on the next turn.
        if conversation_history and conversation_history[-1].role == 'user':
            print("Removing last user turn from history due to error.")
            conversation_history.pop()

    # --- History Management Note ---
    # For very long conversations, you might need to implement logic here
    # to prune the conversation_history list to stay within the model's
    # token limits (e.g., 128k for gemini-1.5-pro) and manage memory usage.
    # This could involve keeping only the last N turns, summarizing older
    # parts, or using a sliding window.