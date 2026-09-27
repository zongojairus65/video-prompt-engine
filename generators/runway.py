from models.scene import Scene
from generators.base import VideoGeneratorAdapter
from compiler.prompt_compiler import VideoPromptCompiler
from compiler.i18n import get_labels, DEFAULT_LANGUAGE


class RunwayAdapter(VideoGeneratorAdapter):

    @property
    def name(self) -> str:
        return "runway"

    def compile(self, scene: Scene, language: str = DEFAULT_LANGUAGE) -> str:
        labels = get_labels(language)
        prompt = VideoPromptCompiler().compile(scene, language)

        return (
            f"{labels['video_target']}: RUNWAY\n"
            f"{labels['preserve_actions']}\n"
            + prompt
        )
