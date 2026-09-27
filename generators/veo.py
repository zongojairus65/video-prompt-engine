from models.scene import Scene
from generators.base import VideoGeneratorAdapter
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.i18n import get_labels, DEFAULT_LANGUAGE


class VeoAdapter(VideoGeneratorAdapter):

    @property
    def name(self) -> str:
        return "veo"

    def compile(self, scene: Scene, language: str = DEFAULT_LANGUAGE) -> str:
        labels = get_labels(language)
        prompt = VideoPromptCompiler().compile(scene, language)

        return (
            f"{labels['video_target']}: GOOGLE VEO\n"
            f"{labels['preserve_actions']}\n"
            + prompt
        )
