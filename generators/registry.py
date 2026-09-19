from generators.base import VideoGeneratorAdapter
from generators.generic import GenericAdapter
from generators.veo import VeoAdapter
from generators.kling import KlingAdapter
from generators.runway import RunwayAdapter


class GeneratorRegistry:

    def __init__(self):
        self._generators: dict[str, VideoGeneratorAdapter] = {
            "generic": GenericAdapter(),
            "veo": VeoAdapter(),
            "kling": KlingAdapter(),
            "runway": RunwayAdapter(),
        }

    def get(self, name: str) -> VideoGeneratorAdapter:
        key = name.lower().strip()

        if key not in self._generators:
            raise ValueError(
                f"Unsupported video generator: {name}"
            )

        return self._generators[key]

    def available(self) -> list[str]:
        return list(self._generators.keys())
