from models.scene import Scene
from generators.base import VideoGeneratorAdapter
from compiler.prompt_compiler import VideoPromptCompiler


class GenericAdapter(VideoGeneratorAdapter):

    @property
    def name(self) -> str:
        return "generic"

    def compile(self, scene: Scene) -> str:
        return VideoPromptCompiler().compile(scene)
