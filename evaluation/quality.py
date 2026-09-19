from models.scene import Scene


class QualityEngine:

    def calculate(self, scene: Scene) -> dict:
        checks = {
            "subjects": bool(scene.subjects),
            "actions": bool(scene.actions),
            "camera": self._camera_quality(scene),
            "animation": self._animation_quality(scene),
            "technical": self._technical_quality(scene),
            "dialogue": self._dialogue_quality(scene),
        }

        score = sum(checks.values()) / len(checks) * 100

        return {
            "score": round(score, 2),
            "checks": checks
        }

    def _camera_quality(self, scene: Scene) -> bool:
        camera = scene.camera

        return any([
            camera.shot,
            camera.movement,
            camera.direction,
            camera.framing,
            camera.tracking
        ])

    def _animation_quality(self, scene: Scene) -> bool:
        animation = scene.animation

        return all([
            animation.character_motion is not None,
            animation.head_movement is not None,
            animation.eyes_movement is not None,
            animation.facial_animation is not None,
            animation.mouth_animation is not None
        ])

    def _technical_quality(self, scene: Scene) -> bool:
        technical = scene.technical

        return bool(
            technical.fps
            and technical.aspect_ratio
            and technical.temporal_consistency
        )

    def _dialogue_quality(self, scene: Scene) -> bool:
        if not scene.dialogue:
            return True

        return all(
            dialogue.text.strip()
            for dialogue in scene.dialogue
        )
