from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel

from models.scene import Scene
from providers.mistral import MistralSceneParser
from compiler.prompt_compiler import VideoPromptCompiler


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.4.0",
    docs_url=None,
    redoc_url=None
)


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    original_prompt: str
    scene: Scene
    technical_prompt: str


parser = MistralSceneParser()
compiler = VideoPromptCompiler()


@app.get("/")
def root():
    return {
        "name": "Video Prompt Engine",
        "version": "0.4.0",
        "status": "online"
    }


@app.get("/docs", include_in_schema=False)
def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Video Prompt Engine - API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


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
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/scene-schema")
def scene_schema():
    return Scene.model_json_schema()
