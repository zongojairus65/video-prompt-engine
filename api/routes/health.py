from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {
        "name": "Video Prompt Engine",
        "version": "0.6.0",
        "status": "online"
    }


@router.get("/health")
def health():
    return {
        "status": "healthy"
    }
