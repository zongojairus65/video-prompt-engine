import json

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from api.routes.generate import pipeline
from database.repository import save_generation
from core.logging import get_logger


router = APIRouter()
logger = get_logger(__name__)


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


@router.get("/generate/stream")
def generate_stream(
    prompt: str = Query(...),
    generator: str = Query("generic")
):
    """Same pipeline as POST /generate, but streamed stage-by-stage
    over Server-Sent Events so a frontend can animate real progress
    instead of a generic spinner."""

    def event_generator():
        if not prompt.strip():
            yield _sse({
                "stage": "error",
                "detail": "Le prompt ne peut pas être vide."
            })
            return

        try:
            for event in pipeline.run_streaming(prompt, generator):
                if event["stage"] == "complete":
                    result = event["result"]

                    try:
                        save_generation(result)
                    except Exception as db_error:
                        logger.warning(
                            "Failed to persist generation | "
                            "request_id=%s | error=%s",
                            result.get("request_id"),
                            db_error
                        )

                    client_result = dict(result)
                    client_result["scene"] = result["scene"].model_dump()

                    yield _sse({
                        "stage": "complete",
                        "result": client_result
                    })
                else:
                    yield _sse(event)

        except Exception as error:
            yield _sse({
                "stage": "error",
                "detail": str(error)
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
