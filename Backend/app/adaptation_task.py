import traceback

from app.config import STATE_IMAGE_DIR
from app.core.audit_logger import get_logger
from app.core.knowledge import knowledge_base
from app.core.mapek_controller import MAPEKController
from app.services import graph_visualizer
from app.services.file_service import FileService


def run_on_demand_adaptation_cycle(feature_model, scenario_id: int) -> None:
    """Run one MAPE-K cycle for a scenario selected through the control API."""
    logger = get_logger()
    case_number = knowledge_base.increment_execution_counter()
    logger.info(
        "--- START CASE #%s | SCENARIO ID: %s ---",
        case_number,
        scenario_id,
    )
    print(
        f"Received scenario {scenario_id}; starting MAPE-K cycle "
        f"for case {case_number}."
    )
    FileService.clear_artifact_files()

    try:
        controller = MAPEKController()
        controller.run_adaptation_cycle(feature_model, scenario_id, case_number)
        knowledge_base.set_variation_point(controller.get_knowledge())
        knowledge_base.set_adaptation_rule(controller.get_adaptation_rule())
        knowledge_base.set_trace(controller.get_trace())
        print(
            f"Stored {len(knowledge_base.get_trace())} MAPE-K trace events "
            "in the knowledge base."
        )

        variation_point = knowledge_base.get_variation_point()
        if variation_point:
            graph_visualizer.generate_state_visualization(
                variation_point,
                feature_model,
                filename=STATE_IMAGE_DIR,
            )
            logger.info(
                "[CASE #%s] Adaptation cycle and state visualization completed.",
                case_number,
            )
        else:
            logger.warning(
                "[CASE #%s] Adaptation cycle ended without a valid configuration.",
                case_number,
            )
    except Exception as error:
        logger.error(
            "[CASE #%s] Background adaptation task failed: %s",
            case_number,
            error,
            exc_info=True,
        )
        traceback.print_exc()
    finally:
        knowledge_base.set_running(False)
        logger.info("--- END CASE #%s ---", case_number)
        print("The adaptation cycle ended; the system is ready for new requests.")
