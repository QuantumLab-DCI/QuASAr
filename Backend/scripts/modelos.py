import google.generativeai as genai
import os

# Configure the API key (prefer environment variables)
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
genai.configure(api_key="")

print("--- Todos los modelos disponibles ---")
for model in genai.list_models():
  print(model.name)

print("\n--- Modelos que SÍ pueden generar contenido (texto/chat) ---")
for model in genai.list_models():
  # Filter for models that support the "generateContent" method
  if 'generateContent' in model.supported_generation_methods:
    print(model.name)
