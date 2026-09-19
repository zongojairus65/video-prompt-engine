from fastapi import APIRouter

from generators.registry import GeneratorRegistry


router = APIRouter()

registry = GeneratorRegistry()


@router.get("/generators")
def available_generators():
    return {
        "generators": registry.available()
    }
