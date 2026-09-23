import os
import json
import requests

from models.scene import Scene
from providers.schema import SCENE_RESPONSE_SCHEMA


class GemmaSceneParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemma-4-31b-it"
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
- constraints (explicit preservation/negative instructions)

Preserve the user's original intent.
Do not invent unnecessary story elements.
If a field is unknown, omit it entirely instead of setting it to null.

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
            timeout=120
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
                raise RuntimeError(f"No non-thought content part found | raw={data}")

            scene_data = json.loads(text)

            # Some responses wrap the object in a single-element
            # array despite the instruction not to.
            if isinstance(scene_data, list):
                if not scene_data:
                    raise RuntimeError(f"Gemma returned an empty JSON array | raw={data}")
                scene_data = scene_data[0]

            return Scene.model_validate(scene_data)

        except Exception as error:
            raise RuntimeError(
                f"Invalid Gemma Scene response: {error} | raw={data}"
            )
