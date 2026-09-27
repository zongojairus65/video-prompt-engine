from models.scene import Scene
from compiler.i18n import get_labels, DEFAULT_LANGUAGE


class VideoPromptCompiler:

    def compile(self, scene: Scene, language: str = DEFAULT_LANGUAGE) -> str:
        labels = get_labels(language)

        sections = []

        sections.append(self._subjects(scene, labels))
        sections.append(self._actions(scene, labels))
        sections.append(self._dialogue(scene, labels))
        sections.append(self._camera(scene, labels))
        sections.append(self._environment(scene, labels))
        sections.append(self._animation(scene, labels))
        sections.append(self._technical(scene, labels))
        sections.append(self._constraints(scene, labels))

        return "\n".join(section for section in sections if section)

    def _subjects(self, scene: Scene, labels: dict) -> str:
        if not scene.subjects:
            return ""

        lines = [labels["subjects"]]
        for subject in scene.subjects:
            text = subject.name

            if subject.description:
                text += f" — {subject.description}"

            if subject.role:
                text += f" — {labels['role']}: {subject.role}"

            lines.append(f"- {text}")

        return "\n".join(lines)

    def _actions(self, scene: Scene, labels: dict) -> str:
        if not scene.actions:
            return ""

        lines = [labels["actions"]]
        for action in scene.actions:
            line = f"- {action.subject}: {action.action}"

            if action.duration is not None:
                line += f" ({action.duration}s)"

            lines.append(line)

        return "\n".join(lines)

    def _dialogue(self, scene: Scene, labels: dict) -> str:
        if not scene.dialogue:
            return ""

        lines = [labels["dialogue"]]

        for dialogue in scene.dialogue:
            # dialogue.text and dialogue.language are content, not
            # UI structure — never localized, rendered verbatim.
            line = f'- "{dialogue.text}"'

            if dialogue.speaker:
                line += f" — {labels['speaker']}: {dialogue.speaker}"

            if dialogue.language:
                line += f" — {labels['language']}: {dialogue.language}"

            if dialogue.lip_sync:
                line += f" — {labels['lip_sync']}"

            voice = dialogue.voice
            voice_parts = [f"{labels['speed']}={voice.speed}x"]

            if voice.gender:
                voice_parts.append(f"{labels['gender']}={voice.gender}")

            if voice.type:
                voice_parts.append(f"{labels['type']}={voice.type}")

            if voice.pitch:
                voice_parts.append(f"{labels['pitch']}={voice.pitch}")

            if voice.tone:
                voice_parts.append(f"{labels['tone']}={voice.tone}")

            if voice.emotion:
                voice_parts.append(f"{labels['emotion']}={voice.emotion}")

            if voice.accent:
                voice_parts.append(f"{labels['accent']}={voice.accent}")

            line += " — voice(" + ", ".join(voice_parts) + ")"

            lines.append(line)

        return "\n".join(lines)

    def _camera(self, scene: Scene, labels: dict) -> str:
        camera = scene.camera
        parts = []

        if camera.shot:
            parts.append(f"{labels['shot']}={camera.shot}")

        if camera.movement:
            parts.append(f"{labels['movement']}={camera.movement}")

        if camera.direction:
            parts.append(f"{labels['direction']}={camera.direction}")

        if camera.framing:
            parts.append(f"{labels['framing']}={camera.framing}")

        if camera.tracking:
            parts.append(f"{labels['tracking']}=true")

        parts.append(f"{labels['speed']}={camera.speed}")

        return labels["camera"] + " " + ", ".join(parts)

    def _environment(self, scene: Scene, labels: dict) -> str:
        environment = scene.environment
        parts = []

        if environment.location:
            parts.append(f"{labels['location']}={environment.location}")

        if environment.time_of_day:
            parts.append(
                f"{labels['time_of_day']}={environment.time_of_day}"
            )

        if environment.weather:
            parts.append(f"{labels['weather']}={environment.weather}")

        if environment.description:
            parts.append(environment.description)

        parts.append(
            f"{labels['background_motion']}={environment.background_motion}"
        )

        return labels["environment"] + " " + ", ".join(parts)

    def _animation(self, scene: Scene, labels: dict) -> str:
        animation = scene.animation

        return (
            labels["animation"] + " "
            f"{labels['character_motion']}={animation.character_motion}, "
            f"{labels['head_movement']}={animation.head_movement}, "
            f"{labels['eyes_movement']}={animation.eyes_movement}, "
            f"{labels['facial_animation']}={animation.facial_animation}, "
            f"{labels['mouth_animation']}={animation.mouth_animation}"
        )

    def _technical(self, scene: Scene, labels: dict) -> str:
        technical = scene.technical

        return (
            labels["technical"] + " "
            f"{labels['fps']}={technical.fps}, "
            f"{labels['aspect_ratio']}={technical.aspect_ratio}, "
            f"{labels['temporal_consistency']}="
            f"{technical.temporal_consistency}"
        )

    def _constraints(self, scene: Scene, labels: dict) -> str:
        if not scene.constraints:
            return ""

        lines = [labels["constraints"]]

        for constraint in scene.constraints:
            lines.append(f"- {constraint}")

        return "\n".join(lines)
