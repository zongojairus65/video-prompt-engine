from evaluation.fidelity import FidelityEngine
from evaluation.semantic_fidelity import SemanticFidelityEngine
from evaluation.quality import QualityEngine
from models.scene import Scene


class EvaluationEngine:

    def __init__(self):
        self.fidelity = FidelityEngine()
        self.semantic = SemanticFidelityEngine()
        self.quality = QualityEngine()

    def evaluate(self, original_prompt: str, scene: Scene) -> dict:
        lexical = self.fidelity.calculate(
            original_prompt,
            scene
        )

        semantic = self.semantic.calculate(
            original_prompt,
            scene
        )

        quality = self.quality.calculate(scene)

        semantic_score = semantic

        fidelity_score = (
            lexical["score"] * 0.4
            + semantic_score * 0.6
        )

        return {
            "fidelity": round(fidelity_score, 2),
            "fidelity_lexical": lexical["score"],
            "fidelity_semantic": semantic_score,
            "quality": quality["score"],
            "quality_details": quality["checks"]
        }
