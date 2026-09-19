import os
import json
import requests

from models.scene import Scene
from providers.schema import SCENE_RESPONSE_SCHEMA


class GemmaSceneParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemma-4-26b-a4b-it"
        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )

    def parse(self, prompt: str) -> Scene:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        instruction = """
You are a professional cinematic video prompt parser.

Convert the user's video instruction into a structured Scene.

Extract:
- subjects
- actions
- dialogue
- camera
- environment (location, time_of_day, weather when mentioned)
- animation
- technical parameters
- voice characteristics

Preserve the user's original intent.
Do not invent unnecessary story elements.
If a field is unknown, omit it entirely instead of setting it to null.
"""

        full_prompt = f"""
{instruction}

USER VIDEO INSTRUCTION:
{prompt}
"""

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": SCENE_RESPONSE_SCHEMA
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
                f"Gemma API error: {response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        try:
            candidate = data["candidates"][0]
            parts = candidate["content"]["parts"]

            # Gemma's "thinking" traces are returned as separate
            # parts flagged thought=True. The actual answer is the
            # first part that isn't a thought.
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

            # Some responses wrap the object in a single-element
            # array despite the instruction not to.
            if isinstance(scene_data, list):
                if not scene_data:
                    raise RuntimeError("Gemma returned an empty JSON array")
                scene_data = scene_data[0]

            return Scene.model_validate(scene_data)

        except Exception as error:
            raise RuntimeError(
                f"Invalid Gemma Scene response: {error} | raw={data}"
            )
