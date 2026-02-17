import os
import google.generativeai as genai
import json
from app.core.audit_logger import get_logger

# 1. Configura el cliente de Google
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"AGENTE_ERROR: Config API fallida: {e}")

def obtener_configuracion_llm(contexto_actual: str, reglas_del_modelo: str) -> dict:
    """
    Agente especializado con Prompting Reforzado para Dependencias Cruzadas.
    """
    logger = get_logger()
    
    # --- PROMPT DE SISTEMA BLINDADO V2 ---
    prompt_sistema = f"""
    Eres el **Motor de Inferencia de Configuración** de un sistema crítico MAPE-K.
    Tu objetivo es generar un JSON válido que cumpla estrictamente el Modelo de Características.

    --- REGLAS DEL MODELO ---
    {reglas_del_modelo}
    --- FIN REGLAS ---

    **REGLAS DE INTEGRIDAD CRÍTICAS (MEMORIZAR):**
    
    1. **Jerarquía (Padres/Hijos):**
       - Si activas un HIJO, debes activar a su PADRE y ABUELO.
       - Ejemplo: Si "cirq_simulator"=true -> ENTONCES "backend"=true Y "hqc"=true.
    
    2. **Dependencias Cruzadas (REQUIERE):**
       - **Regla A:** Si activas "ambientes_abiertos" -> OBLIGATORIAMENTE activa "deportes" (aunque el usuario no lo pida).
       - **Regla B:** Si activas "ambientes_cerrados" -> OBLIGATORIAMENTE activa "visualizador_restriccion_uso_lena".
       - **Regla C:** Si activas "optimizacion_de_rutas" -> OBLIGATORIAMENTE activa "hqc" (y toda su rama).

    3. **Completitud:**
       - Devuelve TODAS las claves del sistema. Usa snake_case.

    **EJEMPLO DE RAZONAMIENTO CORRECTO (CONFLICTO RESUELTO):**
    Usuario: "Perfil: Familia (No quiere deportes). Clima: Bueno (Permite Aire Libre)."
    Asistente:
    {{
        "configuracion": {{
            "gestor_aire": true,
            "turismo": true,
            "ambientes_abiertos": true,
            "deportes": true, 
            "ambientes_cerrados": false
            ...
        }},
        "razonamiento": "Aunque el perfil es Familia, activar 'Ambientes Abiertos' fuerza la activación técnica de 'Deportes' por regla de dependencia."
    }}
    """

    prompt_usuario = f"""
    --- TU TURNO ---
    Contexto en tiempo real:
    {contexto_actual}

    Genera el JSON. Si hay conflicto entre Usuario y Reglas Técnicas, PRIORIZA LAS REGLAS TÉCNICAS.
    """

    print("AGENTE: Analizando escenario con Gemini (Modo Estricto V2)...")

    try:
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.0, # Cero creatividad para máxima obediencia
            top_p=0.8,
            top_k=40
        )
        
        model = genai.GenerativeModel(
            'models/gemini-2.5-flash-lite',
            system_instruction=prompt_sistema,
            generation_config=generation_config
        )

        response = model.generate_content(prompt_usuario)
        
        if not response.parts:
             return {}
        
        data = json.loads(response.text)
        config = data.get("configuracion", {})
        
        # --- SAFETY NET (RED DE SEGURIDAD PYTHON) ---
        # 1. Corrección de Jerarquía
        if config.get("qiskit_simulator") or config.get("cirq_simulator"):
            config["backend"] = True
        if config.get("qaoa") or config.get("vqe"):
            config["algoritmo"] = True
        if config.get("backend") or config.get("algoritmo") or config.get("optimizacion_de_rutas"):
            config["hqc"] = True
            
        # 2. Corrección de Dependencias Cruzadas (Lo que falló en tu log)
        if config.get("ambientes_abiertos"):
            if not config.get("deportes"):
                print("AGENTE_WARN: Auto-corrigiendo -> Activando 'deportes' requerido por 'ambientes_abiertos'.")
                config["deportes"] = True

        if config.get("ambientes_cerrados"):
            if not config.get("visualizador_restriccion_uso_lena"):
                print("AGENTE_WARN: Auto-corrigiendo -> Activando 'visualizador_restriccion_uso_lena'.")
                config["visualizador_restriccion_uso_lena"] = True

        return data

    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO LLM: {str(e)}")
        return {}