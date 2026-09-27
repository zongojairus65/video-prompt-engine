from models.scene import Scene
from compiler.i18n import get_labels, DEFAULT_LANGUAGE


class PromptOptimizer:

    def optimize(
        self,
        prompt: str,
        scene: Scene,
        language: str = DEFAULT_LANGUAGE
    ) -> str:
        labels = get_labels(language)

        sections = []

        prompt = self._clean(prompt)

        if prompt:
            sections.append(prompt)

        sections.append(self._motion_constraints(scene, labels))
        sections.append(self._dialogue_constraints(scene, labels))
        sections.append(self._camera_constraints(scene, labels))
        sections.append(self._technical_constraints(scene, labels))
        sections.append(self._preservation_constraints(scene, labels))

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

    def _motion_constraints(self, scene: Scene, labels: dict) -> str:
        animation = scene.animation

        return (
            labels["motion_constraints"] + " "
            f"{labels['character_motion']}={animation.character_motion}; "
            f"{labels['head_movement']}={animation.head_movement}; "
            f"{labels['eyes_movement']}={animation.eyes_movement}; "
            f"{labels['facial_animation']}={animation.facial_animation}; "
            f"{labels['mouth_animation']}={animation.mouth_animation}"
        )

    def _dialogue_constraints(self, scene: Scene, labels: dict) -> str:
        if not scene.dialogue:
            return ""

        lip_sync = any(
            dialogue.lip_sync
            for dialogue in scene.dialogue
        )

        if lip_sync:
            return (
                labels["dialogue_constraints"] + " "
                f"{labels['preserve_dialogue_text']}; "
                f"{labels['precise_lip_sync_long']}"
            )

        return (
            labels["dialogue_constraints"] + " "
            + labels["preserve_dialogue_text"]
        )

    def _camera_constraints(self, scene: Scene, labels: dict) -> str:
        camera = scene.camera

        constraints = []

        if camera.movement:
            constraints.append(
                f"{labels['movement']}={camera.movement}"
            )

        if camera.direction:
            constraints.append(
                f"{labels['direction']}={camera.direction}"
            )

        if camera.tracking:
            constraints.append(f"{labels['tracking']}=true")

        if not constraints:
            return ""

        return (
            labels["camera_constraints"] + " "
            + "; ".join(constraints)
        )

    def _technical_constraints(self, scene: Scene, labels: dict) -> str:
        technical = scene.technical

        return (
            labels["technical_constraints"] + " "
            f"{labels['fps']}={technical.fps}; "
            f"{labels['aspect_ratio']}={technical.aspect_ratio}; "
            f"{labels['temporal_consistency']}="
            f"{technical.temporal_consistency}"
        )

    def _preservation_constraints(self, scene: Scene, labels: dict) -> str:
        if not scene.constraints:
            return ""

        return (
            labels["preservation_constraints"] + " "
            + "; ".join(scene.constraints)
        )
