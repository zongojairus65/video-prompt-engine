from models.scene import Scene


class VideoPromptCompiler:

    def compile(self, scene: Scene) -> str:
        sections = []

        sections.append(self._subjects(scene))
        sections.append(self._actions(scene))
        sections.append(self._dialogue(scene))
        sections.append(self._camera(scene))
        sections.append(self._environment(scene))
        sections.append(self._animation(scene))
        sections.append(self._technical(scene))

        return "\n".join(section for section in sections if section)

    def _subjects(self, scene: Scene) -> str:
        if not scene.subjects:
            return ""

        lines = ["SUBJECTS:"]
        for subject in scene.subjects:
            text = subject.name

            if subject.description:
                text += f" — {subject.description}"

            if subject.role:
                text += f" — role: {subject.role}"

            lines.append(f"- {text}")

        return "\n".join(lines)

    def _actions(self, scene: Scene) -> str:
        if not scene.actions:
            return ""

        lines = ["ACTIONS:"]
        for action in scene.actions:
            line = f"- {action.subject}: {action.action}"

            if action.duration is not None:
                line += f" ({action.duration}s)"

            lines.append(line)

        return "\n".join(lines)

    def _dialogue(self, scene: Scene) -> str:
        if not scene.dialogue:
            return ""

        lines = ["DIALOGUE:"]

        for dialogue in scene.dialogue:
            line = f'- "{dialogue.text}"'

            if dialogue.speaker:
                line += f" — speaker: {dialogue.speaker}"

            if dialogue.language:
                line += f" — language: {dialogue.language}"

            if dialogue.lip_sync:
                line += " — precise lip sync"

            lines.append(line)

        return "\n".join(lines)

    def _camera(self, scene: Scene) -> str:
        camera = scene.camera
        parts = []

        if camera.shot:
            parts.append(f"shot={camera.shot}")

        if camera.movement:
            parts.append(f"movement={camera.movement}")

        if camera.direction:
            parts.append(f"direction={camera.direction}")

        if camera.framing:
            parts.append(f"framing={camera.framing}")

        if camera.tracking:
            parts.append("tracking=true")

        parts.append(f"speed={camera.speed}")

        return "CAMERA: " + ", ".join(parts)

    def _environment(self, scene: Scene) -> str:
        environment = scene.environment
        parts = []

        if environment.location:
            parts.append(f"location={environment.location}")

        if environment.description:
            parts.append(environment.description)

        parts.append(
            f"background_motion={environment.background_motion}"
        )

        return "ENVIRONMENT: " + ", ".join(parts)

    def _animation(self, scene: Scene) -> str:
        animation = scene.animation

        return (
            "ANIMATION: "
            f"character_motion={animation.character_motion}, "
            f"head_movement={animation.head_movement}, "
            f"eyes_movement={animation.eyes_movement}, "
            f"facial_animation={animation.facial_animation}, "
            f"mouth_animation={animation.mouth_animation}"
        )

    def _technical(self, scene: Scene) -> str:
        technical = scene.technical

        return (
            "TECHNICAL: "
            f"FPS={technical.fps}, "
            f"aspect_ratio={technical.aspect_ratio}, "
            f"temporal_consistency={technical.temporal_consistency}"
        )
