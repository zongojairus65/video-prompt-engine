from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.scene import Scene
from services.pipeline import VideoPromptPipeline
from database.repository import save_generation
from core.logging import get_logger


router = APIRouter()
logger = get_logger(__name__)

pipeline = VideoPromptPipeline()


class PromptRequest(BaseModel):
    prompt: str
    generator: str = "generic"
    mode: str = "text_to_video"  # or "image_to_video"
    fps: Optional[int] = None
    aspect_ratio: Optional[str] = None
    voice_speed: Optional[float] = None


class PromptResponse(BaseModel):
    original_prompt: str
    generator: str
    mode: str
    animation_framing_added: bool
    scene: Scene
    technical_prompt: str
    optimized_prompt: str
    generator_prompt: str
    evaluation: dict


@router.post("/generate", response_model=PromptResponse)
def generate_prompt(request: PromptRequest):
    try:
        if not request.prompt.strip():
            raise ValueError("The video prompt cannot be empty.")

        overrides = {
            "fps": request.fps,
            "aspect_ratio": request.aspect_ratio,
            "voice_speed": request.voice_speed,
        }

        result = pipeline.run(
            request.prompt,
            request.generator,
            overrides,
            request.mode
        )

        try:
            save_generation(result)
        except Exception as db_error:
            logger.warning(
                "Failed to persist generation | request_id=%s | error=%s",
                result.get("request_id"),
                db_error
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
