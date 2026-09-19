from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.scene import Scene
from services.pipeline import VideoPromptPipeline


router = APIRouter()

pipeline = VideoPromptPipeline()


class PromptRequest(BaseModel):
    prompt: str
    generator: str = "generic"


class PromptResponse(BaseModel):
    original_prompt: str
    generator: str
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

        return pipeline.run(
            request.prompt,
            request.generator
        )

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
