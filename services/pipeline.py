import time
import uuid

from core.cache import PromptCache
from core.logging import get_logger
from providers.mistral import MistralSceneParser
from compiler.motion_engine import MotionEngine
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.prompt_optimizer import PromptOptimizer
from evaluation.evaluation_engine import EvaluationEngine
from generators.registry import GeneratorRegistry


logger = get_logger(__name__)


class VideoPromptPipeline:

    def __init__(self):
        self.parser = MistralSceneParser()
        self.motion_engine = MotionEngine()
        self.compiler = VideoPromptCompiler()
        self.optimizer = PromptOptimizer()
        self.evaluator = EvaluationEngine()
        self.generators = GeneratorRegistry()
        self.cache = PromptCache(ttl_seconds=3600)

    def run(
        self,
        user_prompt: str,
        generator: str = "generic"
    ) -> dict:

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

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

            return result

        logger.info(
            "Cache miss | request_id=%s | generator=%s",
            request_id,
            generator
        )

        scene = self.parser.parse(user_prompt)

        scene = self.motion_engine.enrich(scene)

        technical_prompt = self.compiler.compile(scene)

        optimized_prompt = self.optimizer.optimize(
            technical_prompt,
            scene
        )

        adapter = self.generators.get(generator)

        generator_prompt = adapter.compile(scene)

        evaluation = self.evaluator.evaluate(
            user_prompt,
            scene
        )

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

        return result
