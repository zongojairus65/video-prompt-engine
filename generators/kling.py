from models.scene import Scene
from generators.base import VideoGeneratorAdapter
from compiler.prompt_compiler import VideoPromptCompiler


class KlingAdapter(VideoGeneratorAdapter):

    @property
    def name(self) -> str:
        return "kling"

    def compile(self, scene: Scene) -> str:
        prompt = VideoPromptCompiler().compile(scene)

        return (
            "VIDEO GENERATION TARGET: KLING\n"
            "PRESERVE ALL USER-SPECIFIED ACTIONS AND DIALOGUE.\n"
            + prompt
        )
