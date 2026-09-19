from providers.gemini import GeminiSceneParser
from providers.gemma import GemmaSceneParser
from providers.mistral import MistralSceneParser


class SceneParserRouter:
    def __init__(self):
        self.gemini = GeminiSceneParser()
        self.gemma = GemmaSceneParser()
        self.mistral = MistralSceneParser()

    def parse(self, prompt: str):
        errors = []

        # 1. Gemini
        try:
            return self.gemini.parse(prompt)
        except Exception as error:
            errors.append(f"Gemini: {error}")

        # 2. Gemma
        try:
            return self.gemma.parse(prompt)
        except Exception as error:
            errors.append(f"Gemma: {error}")

        # 3. Mistral
        try:
            return self.mistral.parse(prompt)
        except Exception as error:
            errors.append(f"Mistral: {error}")

        raise RuntimeError(
            "All AI providers failed: " + " | ".join(errors)
        )
