from fastapi import FastAPI

from database.init import init_database
from api.routes import generate, generators, health, history


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.8.0"
)

app.include_router(health.router)
app.include_router(generate.router)
app.include_router(generators.router)
app.include_router(history.router)


@app.on_event("startup")
def on_startup():
    init_database()
