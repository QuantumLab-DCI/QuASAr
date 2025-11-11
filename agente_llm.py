import os
import google.generativeai as genai
import json

# 1. Configura el cliente de Google
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"AGENTE_ERROR: No se pudo configurar la API de Google. ¿Estableciste la variable de entorno 'GOOGLE_API_KEY'? Error: {e}")

def obtener_configuracion_llm(contexto_actual: str, reglas_del_modelo: str) -> dict:
    """
    Toma el contexto y las reglas, y pide a la API de Gemini la configuración óptima.
    """
    
    # --- INICIO DE LA MODIFICACIÓN ---
    # 2. Define el prompt del sistema (más especializado)
    prompt_sistema = f"""
    Eres un agente de IA experto en reconfiguración de software y un **validador lógico estricto**.
    Tu trabajo es analizar un contexto de entrada y generar una configuración de 
    características en formato JSON.

    **Sigue este proceso de 3 pasos:**

    **Paso 1: Analiza el Contexto.**
    Lee el contexto en tiempo real para entender las *metas* del usuario 
    (ej. ICA alto, CP alto).

    **Paso 2: Construye la Configuración.**
    Crea un JSON plano que cumpla TODAS las siguientes reglas del Modelo de Características.
    
    --- REGLAS DEL MODELO ---
    {reglas_del_modelo}
    --- FIN DE REGLAS ---

    **Paso 3: Valida tu trabajo.**
    Antes de responder, verifica tu JSON de salida. Presta especial atención a:
    1.  **Reglas 'Obligatoria':** Si un padre está activo, ¿están sus hijos obligatorios activos?
    2.  **Reglas 'Requiere':** Si 'A' está activo y REQUIERE 'B', ¿está 'B' también activo?
    3.  **Reglas 'XOR' / 'OR':** Si un padre está activo, ¿se cumple la regla del grupo (1 para XOR, 1 o más para OR)?
    4.  **Jerarquía:** Si un padre está inactivo, ¿están todos sus hijos (excepto los de reglas 'Requiere') inactivos?

    **Formato de Salida Obligatorio:**
    - Tu respuesta DEBE ser un único objeto JSON **plano (flat)**.
    - NO uses objetos anidados.
    - Las claves DEBEN ser los nombres de las características en 'snake_case' (ej. 'visualizador_calidad_aire').
    - Los valores DEBEN ser `true` o `false`.
    
    Responde ÚNICAMENTE con el objeto JSON de la configuración final,
    sin ninguna explicación adicional.
    """
    # --- FIN DE LA MODIFICACIÓN ---

    # 3. Define el prompt del usuario (el contexto en tiempo real)
    prompt_usuario = f"""
    Contexto en tiempo real:
    {contexto_actual}

    Por favor, genera la configuración JSON óptima, válida y verificada.
    """

    print("AGENTE: Llamando a la API de Google Gemini con el nuevo contexto...")

    try:
        # 4. Configura el modelo y los ajustes de generación
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
        
        # Usando el modelo 'live' que elegiste
        model = genai.GenerativeModel(
            'models/gemini-pro-latest',
            system_instruction=prompt_sistema,
            generation_config=generation_config
        )

        # 5. Realiza la llamada a la API
        response = model.generate_content(prompt_usuario)
        
        respuesta_json = response.text
        print(f"AGENTE: Respuesta JSON recibida: {respuesta_json}")
        
        # 6. Devuelve la respuesta como un diccionario Python
        return json.loads(respuesta_json)

    except Exception as e:
        print(f"AGENTE_ERROR: No se pudo comunicar con la API de Google. Error: {e}")
        return {} # Devuelve una config vacía en caso de error