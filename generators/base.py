from abc import ABC, abstractmethod
from models.scene import Scene


class VideoGeneratorAdapter(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def compile(self, scene: Scene) -> str:
        pass
