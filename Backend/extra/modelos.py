import google.generativeai as genai
import os

# Configura tu clave API (mejor usar variables de entorno)
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyBvAXHZNiGElB8_XC8oDD6Ep1Te6j6W_OQ")

print("--- Todos los modelos disponibles ---")
for model in genai.list_models():
  print(model.name)

print("\n--- Modelos que SÍ pueden generar contenido (texto/chat) ---")
for model in genai.list_models():
  # Filtramos por los que soportan el método "generateContent"
  if 'generateContent' in model.supported_generation_methods:
    print(model.name)