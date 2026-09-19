from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator


class VoiceProfile(BaseModel):
    type: Optional[str] = None
    gender: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.1, le=4.0)
    pitch: Optional[str] = None
    tone: Optional[str] = None
    emotion: Optional[str] = None
    accent: Optional[str] = None


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
    voice: VoiceProfile = Field(default_factory=VoiceProfile)


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
    subjects: List[Subject] = Field(default_factory=list)
    actions: List[Action] = Field(default_factory=list)
    dialogue: List[Dialogue] = Field(default_factory=list)
    camera: Camera = Field(default_factory=Camera)
    environment: Environment = Field(default_factory=Environment)
    animation: Animation = Field(default_factory=Animation)
    technical: Technical = Field(default_factory=Technical)

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls(cls, data: Any) -> Any:
        """LLM providers sometimes emit explicit `null` for an empty
        field instead of omitting it or using [] / {}. Pydantic only
        applies default_factory when the key is absent, not when it
        is present with a null value, so we normalize here before
        validation instead of trusting every provider to be strict."""
        if not isinstance(data, dict):
            return data

        list_fields = ("subjects", "actions", "dialogue")
        object_fields = ("camera", "environment", "animation", "technical")

        for field in list_fields:
            if data.get(field) is None:
                data[field] = []

        for field in object_fields:
            if data.get(field) is None:
                data[field] = {}

        return data
