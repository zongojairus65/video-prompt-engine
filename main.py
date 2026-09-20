from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database.init import init_database
from api.routes import debug, generate, generate_stream, generators, health, history


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.8.0"
)

app.include_router(health.router)
app.include_router(generate.router)
app.include_router(generate_stream.router)
app.include_router(generators.router)
app.include_router(history.router)
app.include_router(debug.router)

app.mount("/app", StaticFiles(directory="static", html=True), name="frontend")


@app.on_event("startup")
def on_startup():
    init_database()
