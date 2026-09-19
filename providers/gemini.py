import os
import json
import requests

from models.scene import Scene


class GeminiSceneParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-flash-latest"
        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )

    def parse(self, prompt: str) -> Scene:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        system_prompt = """
You are a professional cinematic video prompt parser.

Convert the user's short video instruction into a structured Scene.

Extract:
- subjects
- actions
- dialogue
- camera
- environment
- animation
- technical parameters
- voice characteristics

Never invent unnecessary story elements.
Preserve the user's original intent.

Return ONLY a single valid JSON object matching the Scene schema below.
Do NOT wrap it in an array, even for a single scene.
Do NOT include any reasoning, explanation, or markdown fences.

Top-level fields (use exactly these keys):
subjects, actions, dialogue, camera, environment, animation, technical
"""

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "thinkingConfig": {
                    "thinkingLevel": "low"
                }
            }
        }

        response = requests.post(
            self.url,
            params={"key": self.api_key},
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini API error: {response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        try:
            candidate = data["candidates"][0]
            parts = candidate["content"]["parts"]

            text = next(
                (
                    part["text"]
                    for part in parts
                    if part.get("text") and not part.get("thought")
                ),
                None
            )

            if text is None:
                raise RuntimeError("No non-thought content part found")

            scene_data = json.loads(text)

            if isinstance(scene_data, list):
                if not scene_data:
                    raise RuntimeError("Gemini returned an empty JSON array")
                scene_data = scene_data[0]

            return Scene.model_validate(scene_data)

        except Exception as error:
            raise RuntimeError(
                f"Invalid Gemini Scene response: {error} | raw={data}"
            )
