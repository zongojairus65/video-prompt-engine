from models.scene import Scene


class PromptOptimizer:

    def optimize(self, prompt: str, scene: Scene) -> str:
        sections = []

        prompt = self._clean(prompt)

        if prompt:
            sections.append(prompt)

        sections.append(self._motion_constraints(scene))
        sections.append(self._dialogue_constraints(scene))
        sections.append(self._camera_constraints(scene))
        sections.append(self._technical_constraints(scene))
        sections.append(self._preservation_constraints(scene))

        return "\n".join(
            section for section in sections
            if section
        )

    def _clean(self, prompt: str) -> str:
        lines = []

        for line in prompt.splitlines():
            line = " ".join(line.split())

            if line and line not in lines:
                lines.append(line)

        return "\n".join(lines)

    def _motion_constraints(self, scene: Scene) -> str:
        animation = scene.animation

        return (
            "MOTION CONSTRAINTS: "
            f"character_motion={animation.character_motion}; "
            f"head_movement={animation.head_movement}; "
            f"eyes_movement={animation.eyes_movement}; "
            f"facial_animation={animation.facial_animation}; "
            f"mouth_animation={animation.mouth_animation}"
        )

    def _dialogue_constraints(self, scene: Scene) -> str:
        if not scene.dialogue:
            return ""

        lip_sync = any(
            dialogue.lip_sync
            for dialogue in scene.dialogue
        )

        if lip_sync:
            return (
                "DIALOGUE CONSTRAINTS: "
                "preserve exact dialogue text; "
                "precise lip synchronization"
            )

        return "DIALOGUE CONSTRAINTS: preserve exact dialogue text"

    def _camera_constraints(self, scene: Scene) -> str:
        camera = scene.camera

        constraints = []

        if camera.movement:
            constraints.append(
                f"movement={camera.movement}"
            )

        if camera.direction:
            constraints.append(
                f"direction={camera.direction}"
            )

        if camera.tracking:
            constraints.append("tracking=true")

        if not constraints:
            return ""

        return (
            "CAMERA CONSTRAINTS: "
            + "; ".join(constraints)
        )

    def _technical_constraints(self, scene: Scene) -> str:
        technical = scene.technical

        return (
            "TECHNICAL CONSTRAINTS: "
            f"FPS={technical.fps}; "
            f"aspect_ratio={technical.aspect_ratio}; "
            f"temporal_consistency="
            f"{technical.temporal_consistency}"
        )

    def _preservation_constraints(self, scene: Scene) -> str:
        if not scene.constraints:
            return ""

        return (
            "PRESERVATION CONSTRAINTS: "
            + "; ".join(scene.constraints)
        )
