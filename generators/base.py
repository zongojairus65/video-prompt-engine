from abc import ABC, abstractmethod
from models.scene import Scene
from compiler.i18n import DEFAULT_LANGUAGE


class VideoGeneratorAdapter(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def compile(self, scene: Scene, language: str = DEFAULT_LANGUAGE) -> str:
        pass
