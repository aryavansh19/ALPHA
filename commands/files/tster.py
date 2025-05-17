import os
import asyncio
import wave
from google import genai


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash-live-001" # Or "gemini-1.5-flash-latest" or similar

config = {"response_modalities": ["AUDIO"]}

async def main():
    print("Connecting to live session...")
    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            print("Session connected.")


            wf = wave.open("audio.wav", "wb")
            wf.setnchannels(1)       # Mono
            wf.setsampwidth(2)       # 2 bytes = 16 bits
            wf.setframerate(24000)   # 24 kHz

            message = "Hello? Gemini are you there?"
            print(f"Sending message: '{message}'")
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": message}]}, turn_complete=True
            )
            print("Message sent. Receiving audio...")

            audio_data_received = False
            # Corrected loop - use standard async for loop
            async for response in session.receive():
                # Check if the response contains audio data
                if response.data is not None:
                    wf.writeframes(response.data)
                    audio_data_received = True
                    # Optional: Add a print statement to see data arrival
                    # print(".", end="", flush=True) # Print dots as data comes

                #Un-comment this code to print audio data info if needed
                if response.server_content.model_turn is not None:
                     for part in response.server_content.model_turn.parts:
                         if part.inline_data:
                             print(f"\nReceived mime type: {part.inline_data.mime_type}")
                             break # Assume one audio part per turn

            print("\nFinished receiving responses.")

            # Close the WAV file
            wf.close()
            print("Audio saved to audio.wav")

            if not audio_data_received:
                print("Warning: No audio data was received from the API.")


    except NameError:
        print("Error: async_enumerate is not defined. Please use 'async for'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        # In case of error, ensure the file is closed if it was opened
        if 'wf' in locals() and not wf.closed:
             wf.close()


if __name__ == "__main__":
    asyncio.run(main())