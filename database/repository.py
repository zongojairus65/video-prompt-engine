import json

from database.database import SessionLocal
from database.models import Generation


def save_generation(result: dict):

    db = SessionLocal()

    try:
        evaluation = result["evaluation"]

        generation = Generation(
            request_id=result["request_id"],
            original_prompt=result["original_prompt"],
            generator=result["generator"],
            scene_json=json.dumps(
                result["scene"].model_dump(),
                ensure_ascii=False
            ),
            technical_prompt=result["technical_prompt"],
            optimized_prompt=result["optimized_prompt"],
            generator_prompt=result["generator_prompt"],
            fidelity=evaluation["fidelity"],
            quality=evaluation["quality"],
            duration_seconds=result["duration_seconds"],
            cached=int(result.get("cached", False)),
        )

        db.add(generation)
        db.commit()
        db.refresh(generation)

        return generation.id

    finally:
        db.close()
