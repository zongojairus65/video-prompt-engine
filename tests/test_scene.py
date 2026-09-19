from models.scene import (
    Scene,
    Subject,
    Action,
    Dialogue,
)


def test_scene_creation():
    scene = Scene(
        subjects=[
            Subject(
                name="baby",
                description="realistic African baby"
            )
        ],
        actions=[
            Action(
                subject="baby",
                action="raises one hand",
                intensity=0.3
            )
        ],
        dialogue=[
            Dialogue(
                text="Garde la foi.",
                speaker="baby",
                language="fr",
                lip_sync=True
            )
        ]
    )

    assert len(scene.subjects) == 1
    assert len(scene.actions) == 1
    assert len(scene.dialogue) == 1


def test_motion_range():
    scene = Scene()

    assert 0.0 <= scene.animation.character_motion <= 1.0
    assert 0.0 <= scene.animation.mouth_animation <= 1.0


def test_default_technical_settings():
    scene = Scene()

    assert scene.technical.fps == 30
    assert scene.technical.aspect_ratio == "9:16"
