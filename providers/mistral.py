import json

from mistralai.client import Mistral
from config import get_settings
from models.scene import Scene

MODEL = "mistral-medium-latest"

SYSTEM_PROMPT = """
You are the Scene Parser of a professional AI video prompt engine.

Transform the user's video instruction into a structured JSON scene.

IMPORTANT:
- Preserve the user's original intention.
- Do not invent story elements.
- Extract explicit subjects, actions, dialogue, camera instructions,
  environment, animation and audio/voice instructions.
- For environment, extract location, time_of_day (e.g. day, night,
  dusk, dawn) and weather (e.g. rain, light rain, clear, fog, snow)
  whenever the user's instruction mentions them explicitly. Do not
  invent them if not mentioned.
- For dialogue, extract voice type, gender, speed/rate, pitch, tone,
  emotion, accent and language when explicitly provided.
- Preserve explicit voice speed values such as 1.3x exactly.
- Do not invent voice characteristics that the user did not specify.
- If something is unspecified, use neutral defaults.
- Return ONLY valid JSON.
- The result must be compatible with the Scene schema.

Top-level fields:

subjects
actions
dialogue
camera
environment
animation
technical
"""

class MistralSceneParser:
    def __init__(self):
        settings = get_settings()
        self.client = Mistral(api_key=settings.mistral_api_key)

    def parse(self, user_prompt: str) -> Scene:
        if not user_prompt or not user_prompt.strip():
            raise ValueError("The video prompt cannot be empty.")

        response = self.client.chat.complete(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt.strip()},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=3000,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Mistral returned an empty response.")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Mistral returned invalid JSON: {error}")

        try:
            return Scene.model_validate(data)
        except Exception as error:
            raise RuntimeError(f"Scene validation failed: {error}")
