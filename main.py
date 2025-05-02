import os
from google import genai
from google.genai import types


# --- Gemini API Configuration ---

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(model="gemini-2.0-flash")

while(1):
    prompt= input("Enter your prompt: ")
    if prompt=="exit":
        break
    response = chat.send_message(prompt)
    print(response.text)

