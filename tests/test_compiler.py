from compiler.prompt_compiler import VideoPromptCompiler
from models.scene import Scene, Subject, Action


def test_compiler_generates_prompt():
    scene = Scene(
        subjects=[
            Subject(name="baby")
        ],
        actions=[
            Action(
                subject="baby",
                action="raises one hand"
            )
        ]
    )

    result = VideoPromptCompiler().compile(scene)

    assert "SUBJECTS:" in result
    assert "ACTIONS:" in result
    assert "baby" in result
    assert "raises one hand" in result
