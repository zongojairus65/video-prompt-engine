from fastapi import APIRouter
from pydantic import BaseModel

from providers.gemini import GeminiSceneParser
from providers.gemma import GemmaSceneParser
from providers.mistral import MistralSceneParser


router = APIRouter()


class DebugRequest(BaseModel):
    prompt: str


def _try_provider(name: str, parser_factory, prompt: str) -> dict:
    try:
        parser = parser_factory()
        scene = parser.parse(prompt)
        return {
            "provider": name,
            "success": True,
            "scene": scene.model_dump()
        }
    except Exception as error:
        return {
            "provider": name,
            "success": False,
            "error": str(error)
        }


@router.post("/debug/providers")
def debug_providers(request: DebugRequest):
    """Tests Gemini, Gemma and Mistral independently (no fallback,
    no early stop) so a healthy provider earlier in the router chain
    can't hide a broken one behind it."""

    return {
        "gemini": _try_provider(
            "gemini", GeminiSceneParser, request.prompt
        ),
        "gemma": _try_provider(
            "gemma", GemmaSceneParser, request.prompt
        ),
        "mistral": _try_provider(
            "mistral", MistralSceneParser, request.prompt
        ),
    }
