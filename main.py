from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.1.0"
)


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    original_prompt: str
    status: str


@app.get("/")
def root():
    return {
        "name": "Video Prompt Engine",
        "version": "0.1.0",
        "status": "online"
    }


@app.post("/generate", response_model=PromptResponse)
def generate_prompt(request: PromptRequest):
    return PromptResponse(
        original_prompt=request.prompt,
        status="received"
    )
