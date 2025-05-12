import os
import re
from google import genai
from google.genai import types

def create_python_file(filename: str, code_prompt: str, location: str) -> str:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}

    if location not in valid_locations:
        return f"❌ Invalid location '{location}'. Choose from: {', '.join(valid_locations)}"

    if not filename.endswith(".py"):
        filename += ".py"

    file_path = os.path.join(base_user_path, location, filename)
    code_prompt += " JUST GIVE PYTHON CODE WITH MAIN FUNCTION AND WRITE EVERYTHING EXTRA IN COMMENTS"

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[code_prompt]
        )

        if response.text:
            generated_code = response.text

            # Remove ```python and ``` markers using regular expressions
            cleaned_code = re.sub(r"^\s*```(?:python)?\s*", "", generated_code, flags=re.MULTILINE)
            cleaned_code = re.sub(r"\s*```\s*$", "", cleaned_code, flags=re.MULTILINE)

            # Remove leading/trailing empty lines
            cleaned_code = cleaned_code.strip()

            with open(file_path, "w") as f:
                f.write(cleaned_code)
            return f"✅ Python file '{filename}' created at {location} with generated code."
        else:
            return "❌ Error: No code generated."

    except Exception as e:
        return f"❌ Failed to generate and create Python file: {e}"


create_python_file("fibo", "Write a function that takes a number n as input and returns the nth Fibonacci number.", "Desktop")
