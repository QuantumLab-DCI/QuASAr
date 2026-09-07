import json
import os

import google.generativeai as genai

from app.core.audit_logger import get_logger


try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as error:
    print(f"LLM_AGENT_ERROR: API configuration failed: {error}")


def get_llm_configuration(runtime_context: str, feature_model_rules: str) -> dict:
    """Request a constrained configuration, returning empty data on failure."""
    logger = get_logger()
    system_prompt = f"""
    You are the configuration inference engine for a self-adaptive system that
    uses the MAPE-K feedback loop. Generate valid JSON that strictly satisfies
    the hybrid quantum-classical system's feature model.

    --- FEATURE-MODEL RULES ---
    {feature_model_rules}
    --- END FEATURE-MODEL RULES ---

    CRITICAL INTEGRITY RULES:

    1. Hierarchy:
       - Enabling a child requires enabling its parent and ancestors.
       - Example: if "cirq_simulator" is true, "quantum_backend" and
         "hybrid_quantum_computing" must be true.

    2. Cross-tree dependencies and runtime thresholds:
       - If "outdoor_environments" is enabled, enable "sports".
       - If "indoor_environments" is enabled, enable
         "wood_burning_restriction_viewer".
       - If "route_optimization" is enabled, enable
         "hybrid_quantum_computing" and its required branch.
       - If AQI is greater than 150, disable nonessential services, including
         "sports" and "outdoor_environments", regardless of user preference.
       - Enable "route_optimization" and the hybrid quantum-classical branch
         only when problem complexity is greater than 100. Otherwise, retain
         classical execution.
       - When the quantum branch is enabled and the Qiskit queue exceeds 60
         seconds under a latency SLA, select the local "cirq_simulator".
         Otherwise, select "qiskit_simulator".
       - Do not enable an orphaned hybrid quantum-classical branch. It may be
         enabled only when "route_optimization" is enabled.

    3. Completeness:
       - Return every feature key in snake_case.
       - Use only Boolean values for features.

    Required response structure:
    {{
      "configuration": {{
        "air_quality_manager": true,
        "air_quality_viewer": true
      }},
      "reasoning": "Concise technical justification for the adaptation plan."
    }}
    """
    user_prompt = f"""
    Evaluate this real-time runtime context:
    {runtime_context}

    Generate the required JSON. If user preferences conflict with technical
    constraints, prioritize the technical constraints.
    """
    print("LLM_AGENT: Analyzing the runtime scenario with Gemini in strict mode.")

    try:
        generation_config = genai.GenerationConfig(
            temperature=0.0,
            top_p=0.8,
            top_k=40,
        )
        model = genai.GenerativeModel(
            "models/gemini-2.5-flash",
            generation_config=generation_config,
        )
        response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        if not response.parts:
            return {}

        data = json.loads(response.text)
        configuration = data.get("configuration", {})
        if configuration.get("qiskit_simulator") or configuration.get("cirq_simulator"):
            configuration["quantum_backend"] = True
        if configuration.get("qaoa") or configuration.get("vqe"):
            configuration["quantum_algorithm"] = True
        if (
            configuration.get("quantum_backend")
            or configuration.get("quantum_algorithm")
            or configuration.get("route_optimization")
        ):
            configuration["hybrid_quantum_computing"] = True

        if configuration.get("outdoor_environments") and not configuration.get("sports"):
            print("LLM_AGENT_WARNING: Enabling sports required by outdoor_environments.")
            configuration["sports"] = True
        if configuration.get("indoor_environments") and not configuration.get(
            "wood_burning_restriction_viewer"
        ):
            print(
                "LLM_AGENT_WARNING: Enabling wood_burning_restriction_viewer "
                "required by indoor_environments."
            )
            configuration["wood_burning_restriction_viewer"] = True

        if not configuration.get("route_optimization"):
            quantum_features = [
                "hybrid_quantum_computing",
                "quantum_backend",
                "quantum_algorithm",
                "qiskit_simulator",
                "cirq_simulator",
                "qaoa",
                "vqe",
            ]
            corrected = False
            for feature_key in quantum_features:
                if configuration.get(feature_key):
                    configuration[feature_key] = False
                    corrected = True
            if corrected:
                print(
                    "LLM_AGENT_WARNING: Disabled the orphaned hybrid "
                    "quantum-classical branch."
                )
        return data
    except Exception as error:
        logger.error("Critical LLM failure: %s", error)
        return {}
