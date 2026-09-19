import math

from models.scene import Scene
from providers.mistral_embeddings import MistralEmbeddingProvider


class SemanticFidelityEngine:

    def __init__(self):
        self.embedding_provider = MistralEmbeddingProvider()

    def calculate(self, original_prompt: str, scene: Scene) -> float:
        scene_text = self._scene_to_text(scene)

        embeddings = self.embedding_provider.embed([
            original_prompt,
            scene_text
        ])

        similarity = self._cosine_similarity(
            embeddings[0],
            embeddings[1]
        )

        # Convertit approximativement [-1, 1] vers [0, 1]
        normalized = (similarity + 1) / 2

        return round(normalized * 100, 2)

    def _scene_to_text(self, scene: Scene) -> str:
        parts = []

        for subject in scene.subjects:
            parts.append(
                f"subject: {subject.name} {subject.description or ''}"
            )

        for action in scene.actions:
            parts.append(
                f"action: {action.subject} {action.action}"
            )

        for dialogue in scene.dialogue:
            parts.append(
                f"dialogue: {dialogue.text}"
            )

        camera = scene.camera

        parts.append(
            "camera: "
            f"{camera.shot or ''} "
            f"{camera.movement or ''} "
            f"{camera.direction or ''}"
        )

        environment = scene.environment

        parts.append(
            "environment: "
            f"{environment.location or ''} "
            f"{environment.time_of_day or ''} "
            f"{environment.weather or ''} "
            f"{environment.description or ''}"
        )

        return " ".join(parts)

    @staticmethod
    def _cosine_similarity(
        vector_a: list[float],
        vector_b: list[float]
    ) -> float:

        dot = sum(a * b for a, b in zip(vector_a, vector_b))

        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
