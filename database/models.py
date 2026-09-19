from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database.database import Base


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(String, index=True, nullable=False)

    original_prompt = Column(Text, nullable=False)

    generator = Column(String, nullable=False)

    scene_json = Column(Text, nullable=False)

    technical_prompt = Column(Text, nullable=False)

    optimized_prompt = Column(Text, nullable=False)

    generator_prompt = Column(Text, nullable=False)

    fidelity = Column(Float, nullable=False)

    quality = Column(Float, nullable=False)

    duration_seconds = Column(Float, nullable=False)

    cached = Column(Integer, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
