import os

import google.generativeai as genai
from dotenv import load_dotenv

# Configure the API client from the same environment variable used by the backend.
load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

print("--- All available models ---")
for model in genai.list_models():
    print(model.name)

print("\n--- Models that support text or chat content generation ---")
for model in genai.list_models():
    # Retain only models that support the generateContent method.
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
