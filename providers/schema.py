SCENE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "subjects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "role": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "action": {"type": "string"},
                    "intensity": {"type": "number"},
                    "duration": {"type": "number"},
                },
                "required": ["subject", "action"],
            },
        },
        "dialogue": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "speaker": {"type": "string"},
                    "language": {"type": "string"},
                    "lip_sync": {"type": "boolean"},
                    "voice": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "gender": {"type": "string"},
                            "speed": {"type": "number"},
                            "pitch": {"type": "string"},
                            "tone": {"type": "string"},
                            "emotion": {"type": "string"},
                            "accent": {"type": "string"},
                        },
                    },
                },
                "required": ["text"],
            },
        },
        "camera": {
            "type": "object",
            "properties": {
                "shot": {"type": "string"},
                "movement": {"type": "string"},
                "direction": {"type": "string"},
                "speed": {"type": "number"},
                "framing": {"type": "string"},
                "tracking": {"type": "boolean"},
            },
        },
        "environment": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "description": {"type": "string"},
                "time_of_day": {"type": "string"},
                "weather": {"type": "string"},
                "background_motion": {"type": "number"},
            },
        },
        "animation": {
            "type": "object",
            "properties": {
                "character_motion": {"type": "number"},
                "head_movement": {"type": "number"},
                "eyes_movement": {"type": "number"},
                "facial_animation": {"type": "number"},
                "mouth_animation": {"type": "number"},
            },
        },
        "technical": {
            "type": "object",
            "properties": {
                "fps": {"type": "integer"},
                "aspect_ratio": {"type": "string"},
                "temporal_consistency": {"type": "string"},
            },
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "subjects",
        "actions",
        "dialogue",
        "camera",
        "environment",
        "animation",
        "technical",
        "constraints",
    ],
}
