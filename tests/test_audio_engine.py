from compiler.audio_engine import AudioEngine
from models.scene import Dialogue, Scene, VoiceProfile


def test_explicit_voice_speed_is_preserved():

    scene = Scene(
        dialogue=[
            Dialogue(
                text="Bonjour",
                voice=VoiceProfile(
                    type="baby",
                    speed=1.3
                )
            )
        ]
    )

    result = AudioEngine().enrich(scene)

    assert result.dialogue[0].voice.type == "baby"
    assert result.dialogue[0].voice.speed == 1.3


def test_lip_sync_enables_mouth_animation():

    scene = Scene(
        dialogue=[
            Dialogue(
                text="Bonjour",
                lip_sync=True
            )
        ]
    )

    result = AudioEngine().enrich(scene)

    assert result.animation.mouth_animation == 1.0
