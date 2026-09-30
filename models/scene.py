from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# Closed vocabulary for voice.type, chosen only by described age — not
# gender, not personality. Providers are instructed (see providers/*.py
# system prompts) to use exactly one of these, and Gemini/Gemma also
# enforce it structurally via providers/schema.py's enum constraint.
# VOICE_TYPE_SYNONYMS is a fallback safety net for whatever still
# slips through as free text (Mistral in particular has no hard
# schema enforcement) — it normalizes common variants instead of
# either crashing or silently keeping an inconsistent label like
# "young girl voice" when a "baby" was described.
VOICE_TYPES = ("baby", "toddler", "child", "teenager", "adult", "elderly")

VOICE_TYPE_SYNONYMS = {
    "baby": (
        "baby", "infant", "newborn", "bébé", "bebe",
        "nourrisson", "nouveau-né", "nouveau ne"
    ),
    "toddler": ("toddler", "bambin", "tout-petit", "tout petit"),
    "child": (
        "child", "kid", "young girl", "young boy", "little girl",
        "little boy", "enfant", "fillette", "garçonnet", "garconnet"
    ),
    "teenager": ("teenager", "teen", "adolescent", "adolescente", "ado"),
    "adult": ("adult", "man", "woman", "adulte", "homme", "femme"),
    "elderly": (
        "elderly", "old man", "old woman", "senior",
        "âgé", "agé", "âgée", "agee", "personne âgée", "vieillard"
    ),
}


def _normalize_voice_type(raw: str) -> str:
    lowered = raw.strip().lower()

    if lowered in VOICE_TYPES:
        return lowered

    # Check longer, more specific phrases first (e.g. "old woman"
    # before the generic "woman") so a specific synonym in one
    # category isn't shadowed by a shorter generic one in another.
    all_matches = [
        (synonym, canonical)
        for canonical, synonyms in VOICE_TYPE_SYNONYMS.items()
        for synonym in synonyms
    ]
    all_matches.sort(key=lambda pair: len(pair[0]), reverse=True)

    for synonym, canonical in all_matches:
        if synonym in lowered:
            return canonical

    # Unrecognized wording: kept as-is rather than dropped, so a
    # genuinely new case is still visible in output instead of
    # silently disappearing — but it won't match VOICE_TYPES, which
    # is the signal that the vocabulary list may need an entry added.
    return raw


class VoiceProfile(BaseModel):
    type: Optional[str] = None
    gender: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.1, le=4.0)
    pitch: Optional[str] = None
    tone: Optional[str] = None
    emotion: Optional[str] = None
    accent: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, value):
        if value is None:
            return value

        return _normalize_voice_type(str(value))


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
    time_of_day: Optional[str] = None
    weather: Optional[str] = None
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
    constraints: List[str] = Field(default_factory=list)

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

        list_fields = ("subjects", "actions", "dialogue", "constraints")
        object_fields = ("camera", "environment", "animation", "technical")

        for field in list_fields:
            if data.get(field) is None:
                data[field] = []

        for field in object_fields:
            if data.get(field) is None:
                data[field] = {}

        return data
