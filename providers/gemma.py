import os
import json
import requests

from models.scene import Scene


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
- environment
- animation
- technical parameters
- voice characteristics

Preserve the user's original intent.
Do not invent unnecessary story elements.
If information is not specified, use reasonable neutral defaults.

Return ONLY valid JSON matching the Scene schema.
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
                "responseMimeType": "application/json"
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
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            scene_data = json.loads(text)
            return Scene.model_validate(scene_data)

        except Exception as error:
            raise RuntimeError(
                f"Invalid Gemma Scene response: {error} | raw={data}"
            )

