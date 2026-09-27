"""Labels used to render the compiled/optimized prompt structure.

This controls ONLY the section headers and key names in the output
(SUBJECTS/SUJETS, speed=/vitesse=, etc.) — never the actual content:
scene.dialogue[i].text and scene.dialogue[i].language are extracted
values and are rendered verbatim regardless of this setting. A scene
whose dialogue is in French will keep its French dialogue text even
when the surrounding prompt structure is rendered in English, and
vice versa.
"""

LABELS = {
    "en": {
        "subjects": "SUBJECTS:",
        "actions": "ACTIONS:",
        "dialogue": "DIALOGUE:",
        "camera": "CAMERA:",
        "environment": "ENVIRONMENT:",
        "animation": "ANIMATION:",
        "technical": "TECHNICAL:",
        "constraints": "CONSTRAINTS:",
        "role": "role",
        "speaker": "speaker",
        "language": "language",
        "lip_sync": "precise lip sync",
        "location": "location",
        "time_of_day": "time_of_day",
        "weather": "weather",
        "background_motion": "background_motion",
        "shot": "shot",
        "movement": "movement",
        "direction": "direction",
        "framing": "framing",
        "tracking": "tracking",
        "speed": "speed",
        "character_motion": "character_motion",
        "head_movement": "head_movement",
        "eyes_movement": "eyes_movement",
        "facial_animation": "facial_animation",
        "mouth_animation": "mouth_animation",
        "fps": "FPS",
        "aspect_ratio": "aspect_ratio",
        "temporal_consistency": "temporal_consistency",
        "gender": "gender",
        "type": "type",
        "pitch": "pitch",
        "tone": "tone",
        "emotion": "emotion",
        "accent": "accent",
        "motion_constraints": "MOTION CONSTRAINTS:",
        "dialogue_constraints": "DIALOGUE CONSTRAINTS:",
        "camera_constraints": "CAMERA CONSTRAINTS:",
        "technical_constraints": "TECHNICAL CONSTRAINTS:",
        "preservation_constraints": "PRESERVATION CONSTRAINTS:",
        "preserve_dialogue_text": "preserve exact dialogue text",
        "precise_lip_sync_long": "precise lip synchronization",
        "video_target": "VIDEO GENERATION TARGET",
        "preserve_actions": (
            "PRESERVE ALL USER-SPECIFIED ACTIONS AND DIALOGUE."
        ),
    },
    "fr": {
        "subjects": "SUJETS :",
        "actions": "ACTIONS :",
        "dialogue": "DIALOGUE :",
        "camera": "CAMÉRA :",
        "environment": "ENVIRONNEMENT :",
        "animation": "ANIMATION :",
        "technical": "TECHNIQUE :",
        "constraints": "CONTRAINTES :",
        "role": "rôle",
        "speaker": "locuteur",
        "language": "langue",
        "lip_sync": "synchronisation labiale précise",
        "location": "lieu",
        "time_of_day": "moment_journée",
        "weather": "météo",
        "background_motion": "mouvement_arrière_plan",
        "shot": "plan",
        "movement": "mouvement",
        "direction": "direction",
        "framing": "cadrage",
        "tracking": "suivi",
        "speed": "vitesse",
        "character_motion": "mouvement_personnage",
        "head_movement": "mouvement_tête",
        "eyes_movement": "mouvement_yeux",
        "facial_animation": "animation_faciale",
        "mouth_animation": "animation_bouche",
        "fps": "IPS",
        "aspect_ratio": "format_image",
        "temporal_consistency": "cohérence_temporelle",
        "gender": "genre",
        "type": "type",
        "pitch": "hauteur",
        "tone": "ton",
        "emotion": "émotion",
        "accent": "accent",
        "motion_constraints": "CONTRAINTES DE MOUVEMENT :",
        "dialogue_constraints": "CONTRAINTES DE DIALOGUE :",
        "camera_constraints": "CONTRAINTES DE CAMÉRA :",
        "technical_constraints": "CONTRAINTES TECHNIQUES :",
        "preservation_constraints": "CONTRAINTES DE PRÉSERVATION :",
        "preserve_dialogue_text": "préserver le texte exact du dialogue",
        "precise_lip_sync_long": "synchronisation labiale précise",
        "video_target": "CIBLE DE GÉNÉRATION VIDÉO",
        "preserve_actions": (
            "PRÉSERVER TOUTES LES ACTIONS ET DIALOGUES SPÉCIFIÉS "
            "PAR L'UTILISATEUR."
        ),
    },
}

SUPPORTED_LANGUAGES = tuple(LABELS.keys())
DEFAULT_LANGUAGE = "en"


def get_labels(language: str) -> dict:
    return LABELS.get(language, LABELS[DEFAULT_LANGUAGE])
