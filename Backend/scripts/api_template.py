"""Partial FastAPI research template using the English domain contracts."""

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

from app.adaptation_task import run_on_demand_adaptation_cycle
from app.core.feature_model import FeatureModel, build_air_quality_feature_model
from app.core.knowledge import knowledge_base
from app.services.file_service import FileService


app = FastAPI()
feature_model: FeatureModel = build_air_quality_feature_model()
knowledge_base.set_feature_model(feature_model)


class ScenarioSelection(BaseModel):
    scenario_id: int


@app.get("/api/state")
async def get_system_state():
    """Return the same state contract exposed by the active Flask backend."""
    adaptation_rule = knowledge_base.get_adaptation_rule()
    if adaptation_rule is None:
        raise HTTPException(
            status_code=503,
            detail="The system is starting. Select a scenario to run adaptation.",
        )
    variation_point = knowledge_base.get_variation_point()
    configuration = variation_point.get_configuration() if variation_point else {}
    return {
        "context": adaptation_rule,
        "configuration": configuration,
        "current_scenario_id": knowledge_base.get_current_scenario_id(),
        "state_image_url": "/api/static/current_state.png",
        "model_image_url": "/api/static/feature_model.png",
        "quantum_evidence_url": FileService.get_artifact_path(),
        "is_running": knowledge_base.is_running(),
        "mapek_trace": knowledge_base.get_trace(),
    }


@app.get("/api/scenarios")
async def get_scenarios():
    return FileService.read_scenarios()


@app.get("/api/logs")
async def get_logs():
    return {"log_content": FileService.read_logs()}


@app.post("/api/select-scenario")
async def select_scenario(
    selection: ScenarioSelection,
    background_tasks: BackgroundTasks,
):
    """Select a scenario and schedule one on-demand MAPE-K cycle."""
    if knowledge_base.is_running():
        raise HTTPException(
            status_code=423,
            detail="The system is busy. Wait for the current cycle to finish.",
        )
    knowledge_base.set_current_scenario_id(selection.scenario_id)
    knowledge_base.set_running(True)
    background_tasks.add_task(
        run_on_demand_adaptation_cycle,
        feature_model,
        selection.scenario_id,
    )
    return {
        "status": "ok",
        "message": (
            f"Scenario {selection.scenario_id} selected; the adaptation cycle is running."
        ),
        "scenario_id": selection.scenario_id,
    }


@app.get("/api/links/{feature_key}")
async def get_links(feature_key: str):
    variation_point = knowledge_base.get_variation_point()
    if not variation_point:
        raise HTTPException(status_code=503, detail="The system is starting.")
    return variation_point.get_level_configuration(feature_key)


@app.get("/api/link/{feature_key}")
async def get_link(feature_key: str):
    variation_point = knowledge_base.get_variation_point()
    if not variation_point:
        raise HTTPException(status_code=503, detail="The system is starting.")
    return variation_point.get_feature_state(feature_key)


@app.get("/api/adaptation-rule")
async def get_adaptation_rule():
    adaptation_rule = knowledge_base.get_adaptation_rule()
    if adaptation_rule is None:
        raise HTTPException(status_code=503, detail="The system is starting.")
    return {"context": adaptation_rule}
