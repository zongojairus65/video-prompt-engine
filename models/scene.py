from typing import List, Optional
from pydantic import BaseModel, Field


class Subject(BaseModel):
    name: str
    description: Optional[str] = None
    role: Optional[str] = None


class Action(BaseModel):
    subject: str
    action: str
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    duration: Optional[float] = None


class Dialogue(BaseModel):
    text: str
    speaker: Optional[str] = None
    language: Optional[str] = None
    lip_sync: bool = True


class Camera(BaseModel):
    shot: Optional[str] = None
    movement: Optional[str] = None
    direction: Optional[str] = None
    speed: float = Field(default=0.0, ge=0.0, le=1.0)
    framing: Optional[str] = None
    tracking: bool = False


class Environment(BaseModel):
    location: Optional[str] = None
    description: Optional[str] = None
    background_motion: float = Field(default=0.0, ge=0.0, le=1.0)


class Animation(BaseModel):
    character_motion: float = Field(default=0.5, ge=0.0, le=1.0)
    head_movement: float = Field(default=0.5, ge=0.0, le=1.0)
    eyes_movement: float = Field(default=0.5, ge=0.0, le=1.0)
    facial_animation: float = Field(default=0.5, ge=0.0, le=1.0)
    mouth_animation: float = Field(default=1.0, ge=0.0, le=1.0)


class Technical(BaseModel):
    fps: int = 30
    aspect_ratio: str = "9:16"
    temporal_consistency: str = "high"


class Scene(BaseModel):
    subjects: List[Subject] = []
    actions: List[Action] = []
    dialogue: List[Dialogue] = []
    camera: Camera = Camera()
    environment: Environment = Environment()
    animation: Animation = Animation()
    technical: Technical = Technical()
