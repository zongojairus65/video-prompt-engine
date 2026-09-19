from compiler.motion_engine import MotionEngine
from models.scene import Scene, Action


def test_body_freeze():
    scene = Scene(
        actions=[
            Action(
                subject="baby",
                action="parle sans bouger le corps"
            )
        ]
    )

    result = MotionEngine().enrich(scene)

    assert result.animation.character_motion == 0.0
    assert result.animation.head_movement == 0.0


def test_lip_animation():
    scene = Scene(
        actions=[
            Action(
                subject="baby",
                action="seules les lèvres bougent"
            )
        ]
    )

    result = MotionEngine().enrich(scene)

    assert result.animation.character_motion == 0.0
    assert result.animation.mouth_animation == 1.0
