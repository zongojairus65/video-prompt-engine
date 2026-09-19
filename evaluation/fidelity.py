import re
from models.scene import Scene


class FidelityEngine:

    WEIGHTS = {
        "subjects": 0.25,
        "actions": 0.25,
        "relationships": 0.20,
        "environment": 0.10,
        "dialogue": 0.10,
        "intent": 0.10,
    }

    def calculate(self, original_prompt: str, scene: Scene) -> dict:
        text = original_prompt.lower()

        scores = {
            "subjects": self._subject_score(text, scene),
            "actions": self._action_score(text, scene),
            "relationships": self._relationship_score(text, scene),
            "environment": self._environment_score(text, scene),
            "dialogue": self._dialogue_score(text, scene),
            "intent": self._intent_score(text, scene),
        }

        total = sum(
            scores[key] * self.WEIGHTS[key]
            for key in scores
        )

        return {
            "score": round(total * 100, 2),
            "dimensions": {
                key: round(value * 100, 2)
                for key, value in scores.items()
            }
        }

    def _subject_score(self, text: str, scene: Scene) -> float:
        if not scene.subjects:
            return 0.0

        detected = 0

        for subject in scene.subjects:
            if subject.name.lower() in text:
                detected += 1

        return min(detected / len(scene.subjects), 1.0)

    def _action_score(self, text: str, scene: Scene) -> float:
        if not scene.actions:
            return 0.0

        matches = 0

        for action in scene.actions:
            words = self._keywords(action.action)

            if any(word in text for word in words):
                matches += 1

        return matches / len(scene.actions)

    def _relationship_score(self, text: str, scene: Scene) -> float:
        relationship_terms = [
            "pendant que",
            "en même temps",
            "vers la caméra",
            "sans bouger",
            "seulement",
            "tandis que",
        ]

        if not any(term in text for term in relationship_terms):
            return 1.0

        scene_text = str(scene.model_dump()).lower()

        matches = sum(
            1 for term in relationship_terms
            if term in text and (
                term in scene_text
                or any(word in scene_text for word in term.split())
            )
        )

        requested = sum(1 for term in relationship_terms if term in text)

        return matches / requested if requested else 1.0

    def _environment_score(self, text: str, scene: Scene) -> float:
        environment_fields = (
            scene.environment.location,
            scene.environment.description,
            scene.environment.time_of_day,
            scene.environment.weather,
        )

        if not any(environment_fields):
            return 1.0

        environment = " ".join(
            field or "" for field in environment_fields
        ).lower()

        words = self._keywords(environment)

        if not words:
            return 1.0

        matches = sum(1 for word in words if word in text)

        return min(matches / len(words), 1.0)

    def _dialogue_score(self, text: str, scene: Scene) -> float:
        if not scene.dialogue:
            return 1.0

        matches = 0

        for dialogue in scene.dialogue:
            if dialogue.text.lower() in text:
                matches += 1

        return matches / len(scene.dialogue)

    def _intent_score(self, text: str, scene: Scene) -> float:
        if not scene.actions and not scene.dialogue and not scene.subjects:
            return 0.0

        return 1.0

    @staticmethod
    def _keywords(text: str):
        return [
            word
            for word in re.findall(r"\b[\wÀ-ÿ]+\b", text.lower())
            if len(word) > 3
        ]
