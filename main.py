from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models.scene import Scene
from providers.router import SceneParserRouter
from compiler.prompt_compiler import VideoPromptCompiler


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.5.0"
)


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    original_prompt: str
    scene: Scene
    technical_prompt: str


parser = SceneParserRouter()
compiler = VideoPromptCompiler()


@app.get("/")
def root():
    return {
        "name": "Video Prompt Engine",
        "version": "0.5.0",
        "status": "online",
        "providers": [
            "gemini",
            "gemma",
            "mistral"
        ]
    }


@app.post("/generate", response_model=PromptResponse)
def generate_prompt(request: PromptRequest):
    try:
        scene = parser.parse(request.prompt)
        technical_prompt = compiler.compile(scene)

        return PromptResponse(
            original_prompt=request.prompt,
            scene=scene,
            technical_prompt=technical_prompt
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


@app.get("/scene-schema")
def scene_schema():
    return Scene.model_json_schema()
