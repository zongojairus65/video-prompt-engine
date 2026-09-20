import time
import uuid

from core.cache import PromptCache
from core.logging import get_logger
from providers.router import SceneParserRouter
from compiler.motion_engine import MotionEngine
from compiler.audio_engine import AudioEngine
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.prompt_optimizer import PromptOptimizer
from evaluation.evaluation_engine import EvaluationEngine
from generators.registry import GeneratorRegistry


logger = get_logger(__name__)


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

    def run(self, user_prompt: str, generator: str = "generic") -> dict:
        """Non-streaming entry point, kept for callers that just want
        the final result (e.g. the plain /generate route)."""

        result = None

        for event in self.run_streaming(user_prompt, generator):
            if event["stage"] == "complete":
                result = event["result"]

        return result

    def run_streaming(self, user_prompt: str, generator: str = "generic"):
        """Yields one progress event per pipeline stage, then a final
        {"stage": "complete", "result": ...} event. `result["scene"]`
        is a Scene object (not dumped) so callers such as
        database.repository.save_generation can call .model_dump()
        on it directly, matching what the plain run() path already
        assumed before this method existed."""

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        yield {"stage": "cache", "status": "start"}

        cached = self.cache.get(user_prompt, generator)

        if cached is not None:
            logger.info(
                "Cache hit | request_id=%s | generator=%s",
                request_id,
                generator
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
            "Cache miss | request_id=%s | generator=%s",
            request_id,
            generator
        )

        yield {"stage": "parsing", "status": "start"}
        scene = self.parser.parse(user_prompt)
        yield {"stage": "parsing", "status": "done"}

        yield {"stage": "motion", "status": "start"}
        scene = self.motion_engine.enrich(scene)
        yield {"stage": "motion", "status": "done"}

        yield {"stage": "audio", "status": "start"}
        scene = self.audio_engine.enrich(scene)
        yield {"stage": "audio", "status": "done"}

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
            result
        )

        logger.info(
            "Generation completed | request_id=%s | duration=%ss",
            request_id,
            elapsed
        )

        yield {"stage": "complete", "result": result}
