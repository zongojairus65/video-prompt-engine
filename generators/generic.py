from models.scene import Scene
from generators.base import VideoGeneratorAdapter
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.i18n import DEFAULT_LANGUAGE


class GenericAdapter(VideoGeneratorAdapter):

    @property
    def name(self) -> str:
        return "generic"

    def compile(self, scene: Scene, language: str = DEFAULT_LANGUAGE) -> str:
        return VideoPromptCompiler().compile(scene, language)
