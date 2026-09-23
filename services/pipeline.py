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
        mode: str = "text_to_video"
    ) -> dict:
        """Non-streaming entry point, kept for callers that just want
        the final result (e.g. the plain /generate route)."""

        result = None

        for event in self.run_streaming(
            user_prompt,
            generator,
            technical_overrides,
            mode
        ):
            if event["stage"] == "complete":
                result = event["result"]

        return result

    def _apply_overrides(self, scene, technical_overrides: dict) -> None:
        fps_override = technical_overrides.get("fps")
        aspect_override = technical_overrides.get("aspect_ratio")
        voice_speed_override = technical_overrides.get("voice_speed")

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

    def run_streaming(
        self,
        user_prompt: str,
        generator: str = "generic",
        technical_overrides: dict | None = None,
        mode: str = "text_to_video"
    ):
        """Yields one progress event per pipeline stage, then a final
        {"stage": "complete", "result": ...} event. `result["scene"]`
        is a Scene object (not dumped) so callers such as
        database.repository.save_generation can call .model_dump()
        on it directly.

        technical_overrides, if given, is a dict with optional keys:
        "fps" (int), "aspect_ratio" (str), "voice_speed" (float).
        These are applied directly on the extracted Scene after
        parsing, overriding whatever the LLM inferred or defaulted
        to. Deliberately NOT done by asking the LLM to respect these
        values via prompt instructions — an explicit user choice for
        a numeric field must not depend on a model transcribing it
        correctly.

        mode is "text_to_video" (default) or "image_to_video":
        - "image_to_video": if the prompt doesn't already open with
          recognizable animation/preservation framing (see
          compiler.image_to_video), a standard template is prepended
          before parsing. scene.constraints (preservation/negative
          instructions) is extracted normally and rendered in both
          the technical and optimized prompts.
        - "text_to_video": scene.constraints is always cleared after
          parsing, regardless of what the LLM extracted, so it never
          reaches the compiled output. This is a deliberate hard
          gate rather than "just don't render it" — the two states
          must never mix silently.

        Note: a cache hit skips extraction entirely and returns the
        previously computed Scene as-is, overrides included from
        whenever it was cached — a cache hit with different override
        values than the original request will NOT re-apply new
        overrides. This mirrors the existing cache design and is a
        known limitation, not silently swallowed: flagged here for
        whoever touches this next.
        """

        if mode not in VALID_MODES:
            mode = "text_to_video"

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        yield {"stage": "cache", "status": "start"}

        cached = self.cache.get(user_prompt, generator, mode)

        if cached is not None:
            logger.info(
                "Cache hit | request_id=%s | generator=%s | mode=%s",
                request_id,
                generator,
                mode
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
            "Cache miss | request_id=%s | generator=%s | mode=%s",
            request_id,
            generator,
            mode
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
        technical_prompt = self.compiler.compile(scene)
        yield {"stage": "compiling", "status": "done"}

        yield {"stage": "optimizing", "status": "start"}
        optimized_prompt = self.optimizer.optimize(
            technical_prompt,
            scene
        )
        yield {"stage": "optimizing", "status": "done"}

        yield {"stage": "generator", "status": "start"}
        adapter = self.generators.get(generator)
        generator_prompt = adapter.compile(scene)
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
            mode
        )

        logger.info(
            "Generation completed | request_id=%s | duration=%ss",
            request_id,
            elapsed
        )

        yield {"stage": "complete", "result": result}
