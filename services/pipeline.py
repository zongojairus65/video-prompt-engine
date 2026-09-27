import time
import uuid

from core.cache import PromptCache
from core.logging import get_logger
from providers.router import SceneParserRouter
from compiler.motion_engine import MotionEngine
from compiler.audio_engine import AudioEngine
from compiler.image_to_video import ensure_animation_framing
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.prompt_optimizer import PromptOptimizer
from compiler.i18n import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from evaluation.evaluation_engine import EvaluationEngine
from generators.registry import GeneratorRegistry


logger = get_logger(__name__)

# VoiceProfile.speed is declared with ge=0.1, le=4.0 in models/scene.py,
# but pydantic only enforces that on construction/validation — setting
# .speed on an already-built instance does NOT re-validate (no
# validate_assignment on the model). Since we apply overrides via direct
# attribute mutation below, we clamp manually here instead of silently
# trusting the caller.
VOICE_SPEED_MIN = 0.1
VOICE_SPEED_MAX = 4.0

FPS_MIN = 1
FPS_MAX = 240

VALID_MODES = ("text_to_video", "image_to_video")


class VideoPromptPipeline:

    def __init__(self):
        self.parser = SceneParserRouter()
        self.motion_engine = MotionEngine()
        self.audio_engine = AudioEngine()
        self.compiler = VideoPromptCompiler()
        self.optimizer = PromptOptimizer()
        self.evaluator = EvaluationEngine()
        self.generators = GeneratorRegistry()
        self.cache = PromptCache(ttl_seconds=3600)

    def run(
        self,
        user_prompt: str,
        generator: str = "generic",
        technical_overrides: dict | None = None,
        mode: str = "text_to_video",
        prompt_language: str = DEFAULT_LANGUAGE
    ) -> dict:
        """Non-streaming entry point, kept for callers that just want
        the final result (e.g. the plain /generate route)."""

        result = None

        for event in self.run_streaming(
            user_prompt,
            generator,
            technical_overrides,
            mode,
            prompt_language
        ):
            if event["stage"] == "complete":
                result = event["result"]

        return result

    def _apply_overrides(self, scene, technical_overrides: dict) -> None:
        fps_override = technical_overrides.get("fps")
        aspect_override = technical_overrides.get("aspect_ratio")
        voice_speed_override = technical_overrides.get("voice_speed")
        voice_accent_override = technical_overrides.get("voice_accent")

        if fps_override is not None:
            clamped = max(FPS_MIN, min(FPS_MAX, int(fps_override)))
            scene.technical.fps = clamped

        if aspect_override:
            scene.technical.aspect_ratio = aspect_override

        if voice_speed_override is not None:
            clamped_speed = max(
                VOICE_SPEED_MIN,
                min(VOICE_SPEED_MAX, float(voice_speed_override))
            )

            # Applies to every dialogue line uniformly. This is only
            # offered to the user when the prompt has dialogue but no
            # speech-rate wording at all, so overriding all of them
            # is consistent with "none of them had one specified".
            # It cannot express different speeds per character — that
            # still has to be written explicitly in the prompt text.
            for dialogue in scene.dialogue:
                dialogue.voice.speed = clamped_speed

        if voice_accent_override:
            # Same uniform-application logic as voice_speed above:
            # only offered when no dialogue line mentions an accent
            # at all, so applying it to every line is consistent.
            for dialogue in scene.dialogue:
                dialogue.voice.accent = voice_accent_override.strip()

    def run_streaming(
        self,
        user_prompt: str,
        generator: str = "generic",
        technical_overrides: dict | None = None,
        mode: str = "text_to_video",
        prompt_language: str = DEFAULT_LANGUAGE
    ):
        """Yields one progress event per pipeline stage, then a final
        {"stage": "complete", "result": ...} event. `result["scene"]`
        is a Scene object (not dumped) so callers such as
        database.repository.save_generation can call .model_dump()
        on it directly.

        mode is "text_to_video" (default) or "image_to_video" — see
        compiler.image_to_video for what changes.

        prompt_language is "en" (default) or "fr" and controls ONLY
        the rendered structure of technical_prompt/optimized_prompt/
        generator_prompt. It never touches scene.dialogue[i].text or
        scene.dialogue[i].language.
        """

        if mode not in VALID_MODES:
            mode = "text_to_video"

        if prompt_language not in SUPPORTED_LANGUAGES:
            prompt_language = DEFAULT_LANGUAGE

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        yield {"stage": "cache", "status": "start"}

        cached = self.cache.get(user_prompt, generator, mode, prompt_language)

        if cached is not None:
            logger.info(
                "Cache hit | request_id=%s | generator=%s | mode=%s | lang=%s",
                request_id,
                generator,
                mode,
                prompt_language
            )

            result = dict(cached)
            result["request_id"] = request_id
            result["cached"] = True
            result["duration_seconds"] = round(
                time.perf_counter() - start,
                3
            )

            yield {"stage": "cache", "status": "done", "detail": "hit"}
            yield {"stage": "complete", "result": result}
            return

        yield {"stage": "cache", "status": "done", "detail": "miss"}

        logger.info(
            "Cache miss | request_id=%s | generator=%s | mode=%s | lang=%s",
            request_id,
            generator,
            mode,
            prompt_language
        )

        prompt_for_parsing = user_prompt
        animation_framing_added = False

        if mode == "image_to_video":
            prompt_for_parsing, animation_framing_added = (
                ensure_animation_framing(user_prompt)
            )

        yield {"stage": "parsing", "status": "start"}
        scene = self.parser.parse(prompt_for_parsing)
        yield {"stage": "parsing", "status": "done"}

        yield {"stage": "motion", "status": "start"}
        scene = self.motion_engine.enrich(scene)
        yield {"stage": "motion", "status": "done"}

        yield {"stage": "audio", "status": "start"}
        scene = self.audio_engine.enrich(scene)
        yield {"stage": "audio", "status": "done"}

        if mode != "image_to_video":
            scene.constraints = []

        if technical_overrides:
            self._apply_overrides(scene, technical_overrides)

        yield {"stage": "compiling", "status": "start"}
        technical_prompt = self.compiler.compile(scene, prompt_language)
        yield {"stage": "compiling", "status": "done"}

        yield {"stage": "optimizing", "status": "start"}
        optimized_prompt = self.optimizer.optimize(
            technical_prompt,
            scene,
            prompt_language
        )
        yield {"stage": "optimizing", "status": "done"}

        yield {"stage": "generator", "status": "start"}
        adapter = self.generators.get(generator)
        generator_prompt = adapter.compile(scene, prompt_language)
        yield {"stage": "generator", "status": "done"}

        yield {"stage": "evaluating", "status": "start"}
        evaluation = self.evaluator.evaluate(
            user_prompt,
            scene
        )
        yield {"stage": "evaluating", "status": "done"}

        elapsed = round(
            time.perf_counter() - start,
            3
        )

        result = {
            "request_id": request_id,
            "original_prompt": user_prompt,
            "generator": adapter.name,
            "mode": mode,
            "prompt_language": prompt_language,
            "animation_framing_added": animation_framing_added,
            "scene": scene,
            "technical_prompt": technical_prompt,
            "optimized_prompt": optimized_prompt,
            "generator_prompt": generator_prompt,
            "evaluation": evaluation,
            "duration_seconds": elapsed,
            "cached": False,
        }

        self.cache.set(
            user_prompt,
            generator,
            result,
            mode,
            prompt_language
        )

        logger.info(
            "Generation completed | request_id=%s | duration=%ss",
            request_id,
            elapsed
        )

        yield {"stage": "complete", "result": result}
