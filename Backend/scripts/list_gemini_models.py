"""List Gemini models and their content-generation support."""

import os

import google.generativeai as genai
from dotenv import load_dotenv

# Use the same API key as the backend.
load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

print("--- All available models ---")
for model in genai.list_models():
    print(model.name)

print("\n--- Models that support text or chat content generation ---")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
