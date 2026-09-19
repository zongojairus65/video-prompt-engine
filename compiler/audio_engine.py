from models.scene import Scene


class AudioEngine:

    def enrich(self, scene: Scene) -> Scene:

        for dialogue in scene.dialogue:

            voice = dialogue.voice
            text = dialogue.text.lower()

            # Explicit speech-speed semantics
            if "rapidement" in text or "fast" in text:
                if voice.speed == 1.0:
                    voice.speed = 1.25

            if "lentement" in text or "slowly" in text:
                if voice.speed == 1.0:
                    voice.speed = 0.8

            # Explicit baby voice
            if "bébé" in text or "baby" in text:
                if voice.type is None:
                    voice.type = "baby"

            # Explicit adult voice
            if "adulte" in text or "adult" in text:
                if voice.type is None:
                    voice.type = "adult"

            # Lip synchronization
            if dialogue.lip_sync:
                scene.animation.mouth_animation = 1.0

        return scene
