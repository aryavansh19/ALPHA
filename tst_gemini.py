import os
import google.generativeai as genai
from google.genai import types



# --- Define a Simple Dummy Tool ---
# This minimal tool just exists to test if the 'tools' parameter is accepted
dummy_declaration = types.FunctionDeclaration(
    name='dummy_function',
    description='A simple dummy function for testing.',
    parameters={
        'type': 'object',
        'properties': {
            'param1': {'type': 'string', 'description': 'A dummy parameter'}
        },
        'required': ['param1']
    }
)
dummy_tool = types.Tool(function_declarations=[dummy_declaration])

# --- Gemini API Configuration ---
# Make sure your GEMINI_API_KEY environment variable is set correctly

client = genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# --- Gemini API Configuration (Corrected) ---
# Make sure your GEMINI_API_KEY environment variable is set correctly
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit() # Exit if API key is missing

# Configure the API key globally
genai.configure(api_key=api_key)

# --- Get the Generative Model instance ---
# You can pass tools here directly, or in the generate_content call
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[dummy_tool] # Pass the tools when getting the model or in generate_content
)

# --- Gemini API Configuration (Corrected) ---
# Make sure your GEMINI_API_KEY environment variable is set correctly
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit() # Exit if API key is missing

# Configure the API key globally
genai.configure(api_key=api_key)

# --- Get the Generative Model instance ---
# You can pass tools here directly, or in the generate_content call
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[dummy_tool] # Pass the tools when getting the model or in generate_content
)


# --- Attempt generate_content call with the tool ---
try:
    print("\nAttempting model.generate_content with 'tools' parameter...")
    response = model.generate_content( # <--- Call generate_content directly on the model object
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text="Use the dummy function with param1='testvalue'")]
            )
        ]
        # If tools were not passed when creating the model, pass them here:
        # tools=[dummy_tool]
    )

    print("Successfully called generate_content with 'tools'.")

    # Optional: Print response to see if it suggested the dummy function call
    print("\nResponse:")
    # You might need to check response.candidates[0].content.parts[0].function_call
    # depending on the model's response
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
         print(response.candidates[0].content)
    else:
        print("No content in response.")


except TypeError as e:
    print(f"\nCaught an unexpected TypeError: {e}")
    print("This is now unexpected if the client initialization is correct.")
except Exception as e:
    print(f"\nCaught another error: {e}")
    import traceback
    traceback.print_exc()