from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from models.scene import Scene
from providers.mistral import MistralSceneParser
from compiler.prompt_compiler import VideoPromptCompiler


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.4.0",
    docs_url=None,
    redoc_url=None
)


class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    original_prompt: str
    scene: Scene
    technical_prompt: str


parser = MistralSceneParser()
compiler = VideoPromptCompiler()


@app.get("/")
def root():
    return {
        "name": "Video Prompt Engine",
        "version": "0.4.0",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def custom_docs():
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Video Prompt Engine</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #111827;
    color: #f9fafb;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 900px;
    margin: auto;
}
h1 {
    margin-bottom: 5px;
}
p {
    color: #9ca3af;
}
textarea {
    width: 100%;
    min-height: 160px;
    box-sizing: border-box;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #374151;
    background: #1f2937;
    color: white;
    font-size: 16px;
    resize: vertical;
}
button {
    margin-top: 12px;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    font-size: 16px;
    cursor: pointer;
}
button:active {
    opacity: 0.8;
}
pre {
    white-space: pre-wrap;
    word-break: break-word;
    background: #0b1120;
    padding: 15px;
    border-radius: 10px;
    overflow-x: auto;
}
.status {
    margin: 15px 0;
    color: #60a5fa;
}
</style>
</head>

<body>
<div class="container">

<h1>🎬 Video Prompt Engine</h1>
<p>Professional AI video prompt compiler</p>

<h2>Generate Technical Prompt</h2>

<textarea id="prompt"
placeholder="Exemple : A realistic African baby walks toward the camera and says hello..."></textarea>

<br>

<button onclick="generate()">Generate</button>

<div class="status" id="status"></div>

<h2>Result</h2>

<pre id="result">Aucun résultat.</pre>

<h2>API</h2>

<pre>
GET  /
GET  /health
GET  /openapi.json
POST /generate
GET  /scene-schema
</pre>

<script>
async function generate() {

    const prompt = document.getElementById("prompt").value;
    const status = document.getElementById("status");
    const result = document.getElementById("result");

    if (!prompt.trim()) {
        result.textContent = "Veuillez entrer un prompt.";
        return;
    }

    status.textContent = "⏳ Génération en cours...";
    result.textContent = "";

    try {

        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: prompt
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        status.textContent = "✅ Génération terminée";

        result.textContent =
            "TECHNICAL PROMPT\\n\\n" +
            data.technical_prompt +
            "\\n\\n-----------------------------\\n\\n" +
            "SCENE JSON\\n\\n" +
            JSON.stringify(data.scene, null, 2);

    } catch (error) {

        status.textContent = "❌ Erreur";

        result.textContent = error.message;
    }
}
</script>

</div>
</body>
</html>
"""


@app.post("/generate", response_model=PromptResponse)
def generate_prompt(request: PromptRequest):
    try:
        scene = parser.parse(request.prompt)
        technical_prompt = compiler.compile(scene)

        return PromptResponse(
            original_prompt=request.prompt,
            scene=scene,
            technical_prompt=technical_prompt
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/scene-schema")
def scene_schema():
    return Scene.model_json_schema()
