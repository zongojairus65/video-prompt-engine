from models.scene import Scene


class MotionEngine:

    def enrich(self, scene: Scene) -> Scene:
        self._process_actions(scene)
        self._process_camera(scene)
        self._process_dialogue(scene)
        return scene

    def _process_actions(self, scene: Scene):
        for action in scene.actions:
            text = action.action.lower()

            if "marche vers la caméra" in text:
                scene.camera.tracking = True
                scene.camera.direction = "backward"

            if "sans bouger le corps" in text:
                scene.animation.character_motion = 0.0
                scene.animation.head_movement = 0.0

            if "seules les lèvres" in text or "seulement les lèvres" in text:
                scene.animation.character_motion = 0.0
                scene.animation.mouth_animation = 1.0

            if "yeux" in text:
                scene.animation.eyes_movement = 0.5

    def _process_camera(self, scene: Scene):
        camera = scene.camera
        movement = (camera.movement or "").lower()

        if "tourne autour" in movement or "orbit" in movement:
            camera.tracking = True

        if "lentement" in movement:
            camera.speed = min(camera.speed or 0.25, 0.25)

    def _process_dialogue(self, scene: Scene):
        for dialogue in scene.dialogue:
            if dialogue.lip_sync:
                scene.animation.mouth_animation = 1.0
