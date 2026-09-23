import os
import json
import requests

from models.scene import Scene
from providers.schema import SCENE_RESPONSE_SCHEMA

# Newest to oldest, Flash-class only (Pro is paid-only, so it's
# deliberately excluded here). If the first model is overloaded,
# deprecated, or rejects a parameter, we fall through to the next
# one before giving up on Gemini entirely and handing off to
# Gemma/Mistral in providers/router.py.
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

SYSTEM_PROMPT = """
You are a professional cinematic video prompt parser.

Convert the user's short video instruction into a structured Scene.

Extract:
- subjects
- actions
- dialogue
- camera
- environment (location, time_of_day, weather when mentioned)
- animation
- technical parameters
- voice characteristics

Never invent unnecessary story elements.
Preserve the user's original intent.

Return ONLY a single valid JSON object matching the Scene schema below.
Do NOT wrap it in an array, even for a single scene.
Do NOT include any reasoning, explanation, or markdown fences.

Top-level fields (use exactly these keys):
subjects, actions, dialogue, camera, environment, animation, technical, constraints

For environment, extract location, time_of_day (e.g. day, night,
dusk, dawn) and weather (e.g. rain, light rain, clear, fog, snow)
whenever explicitly mentioned. Do not invent them if not mentioned.

For constraints, extract explicit preservation or negative
instructions as a list of short strings — things the user says to
keep unchanged (identity, face, clothing, background, proportions)
or to avoid (distortion, deformation, changing the scene). Only
extract constraints the user actually stated; do not invent generic
ones. If none are stated, return an empty list.
"""


class GeminiSceneParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def _url_for(self, model: str) -> str:
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )

    def _try_model(self, model: str, prompt: str) -> Scene:
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
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
                "responseSchema": SCENE_RESPONSE_SCHEMA,
                "thinkingConfig": {
                    "thinkingLevel": "low"
                }
            }
        }

        response = requests.post(
            self._url_for(model),
            params={"key": self.api_key},
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"{response.status_code} {response.text}"
            )

        data = response.json()

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
            raise RuntimeError(f"No non-thought content part found | raw={data}")

        scene_data = json.loads(text)

        if isinstance(scene_data, list):
            if not scene_data:
                raise RuntimeError(f"Empty JSON array | raw={data}")
            scene_data = scene_data[0]

        return Scene.model_validate(scene_data)

    def parse(self, prompt: str) -> Scene:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        errors = []

        for model in GEMINI_MODELS:
            try:
                return self._try_model(model, prompt)
            except Exception as error:
                errors.append(f"{model}: {error}")

        raise RuntimeError(
            "All Gemini models failed: " + " | ".join(errors)
        )
