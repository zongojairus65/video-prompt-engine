from fastapi import APIRouter, HTTPException
from database.database import SessionLocal
from database.models import Generation


router = APIRouter()


@router.get("/generations")
def list_generations(limit: int = 20):

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100"
        )

    db = SessionLocal()

    try:
        generations = (
            db.query(Generation)
            .order_by(Generation.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "count": len(generations),
            "generations": [
                {
                    "id": item.id,
                    "request_id": item.request_id,
                    "generator": item.generator,
                    "fidelity": item.fidelity,
                    "quality": item.quality,
                    "duration_seconds": item.duration_seconds,
                    "cached": bool(item.cached),
                    "created_at": item.created_at,
                }
                for item in generations
            ]
        }

    finally:
        db.close()


@router.get("/generations/{generation_id}")
def get_generation(generation_id: int):

    db = SessionLocal()

    try:
        generation = (
            db.query(Generation)
            .filter(Generation.id == generation_id)
            .first()
        )

        if generation is None:
            raise HTTPException(
                status_code=404,
                detail="Generation not found"
            )

        return {
            "id": generation.id,
            "request_id": generation.request_id,
            "original_prompt": generation.original_prompt,
            "generator": generation.generator,
            "scene": generation.scene_json,
            "technical_prompt": generation.technical_prompt,
            "optimized_prompt": generation.optimized_prompt,
            "generator_prompt": generation.generator_prompt,
            "fidelity": generation.fidelity,
            "quality": generation.quality,
            "duration_seconds": generation.duration_seconds,
            "cached": bool(generation.cached),
            "created_at": generation.created_at,
        }

    finally:
        db.close()
