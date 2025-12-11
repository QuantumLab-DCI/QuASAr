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
    Incluye capacidad de 'improvisación' y EXPLICACIÓN detallada de decisiones.
    """
    
    # --- INICIO DE LA MODIFICACIÓN: Prompt Explicativo y Resiliente ---
    # 2. Define el prompt del sistema (Arquitecto Explicativo)
    prompt_sistema = f"""
    Eres el **Arquitecto Autónomo Principal** de un sistema híbrido crítico.
    Tu misión es asegurar la continuidad operativa y **JUSTIFICAR TUS DECISIONES TÉCNICAS**.

    Tienes este Modelo de Características (Reglas Ideales):
    --- REGLAS DEL MODELO ---
    {reglas_del_modelo}
    --- FIN DE REGLAS ---

    **PROTOCOLO DE TOMA DE DECISIONES:**
    1. **Analiza:** Lee el contexto completo (Intención del Usuario, Clima, Infraestructura).
    2. **Decide:** Selecciona las características activas basándote en el perfil del usuario y las restricciones ambientales.
    3. **Negocia:** Si hay conflicto crítico (ej. Qiskit saturado), improvisa una solución (Trade-off) y explica por qué.

    **Formato de Salida Obligatorio (JSON):**
    Tu respuesta DEBE ser un objeto JSON con exactamente DOS claves principales:
    1. "configuracion": Un objeto plano con las características (claves snake_case, valores booleanos).
    2. "razonamiento": **CADENA DE TEXTO EXPLICATIVA (Max 50 palabras).**
       - Explica POR QUÉ activaste/desactivaste ramas opcionales (ej. "Activé Deportes por perfil Usuario Deportivo").
       - Explica POR QUÉ elegiste el backend cuántico específico (ej. "Elegí Cirq por saturación crítica en Qiskit").
       - Sé conciso pero específico.

    **Ejemplo de Estructura:**
    {{
        "configuracion": {{ "gestor_aire": true, "deportes": true, "qiskit_simulator": false, "cirq_simulator": true, ... }},
        "razonamiento": "Activé Deportes debido al perfil 'Grupo Deportivo' y buen clima (ICA 40). Seleccioné Cirq Simulator para evitar la cola de 120s en Qiskit."
    }}
    
    Responde ÚNICAMENTE con este objeto JSON.
    """
    # --- FIN DE LA MODIFICACIÓN ---

    # 3. Define el prompt del usuario (el contexto en tiempo real)
    prompt_usuario = f"""
    Contexto en tiempo real (Sensores, Usuario y Colas):
    {contexto_actual}

    Genera la configuración y explica el porqué de tus decisiones clave.
    """

    print("AGENTE: Analizando escenario con Gemini...")

    try:
        # 4. Configura el modelo y los ajustes de generación
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            # Temperatura 0.4 para permitir flexibilidad en la resolución de conflictos y variedad en la explicación
            temperature=0.4 
        )
        
        # Usando el modelo flash (rápido y económico)
        model = genai.GenerativeModel(
            'models/gemini-2.5-flash-lite',
            system_instruction=prompt_sistema,
            generation_config=generation_config
        )

        # 5. Realiza la llamada a la API
        response = model.generate_content(prompt_usuario)
        
        respuesta_json = response.text
        print(f"AGENTE: Respuesta JSON recibida.")
        
        # 6. Devuelve la respuesta como un diccionario Python
        return json.loads(respuesta_json)

    except Exception as e:
        print(f"AGENTE_ERROR: No se pudo comunicar con la API de Google. Error: {e}")
        return {} # Devuelve una config vacía en caso de error