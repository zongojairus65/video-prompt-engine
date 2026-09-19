from fastapi import FastAPI

from core.logging import configure_logging
from api.routes.generate import router as generate_router
from api.routes.health import router as health_router
from api.routes.generators import router as generators_router
from api.routes.history import router as history_router


configure_logging()


app = FastAPI(
    title="Video Prompt Engine",
    description="AI-powered technical video prompt generation engine",
    version="0.8.0"
)

app.include_router(health_router)
app.include_router(generate_router)
app.include_router(generators_router)
app.include_router(history_router)
