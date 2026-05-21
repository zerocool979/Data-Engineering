"""
database/models.py - SQLAlchemy ORM Models
Wildlife Intelligence Monitoring System
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean, Index, create_engine
)
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Animal(Base):
    """Main animals table - core entity of the system."""
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    height_cm = Column(String(50), nullable=True)        # stored as range string
    weight_kg = Column(String(50), nullable=True)
    color = Column(String(100), nullable=True)
    lifespan_years = Column(String(50), nullable=True)
    diet = Column(String(100), nullable=True)
    habitat = Column(String(200), nullable=True, index=True)
    predators = Column(String(300), nullable=True)
    top_speed_kmh = Column(Float, nullable=True)
    countries_found = Column(String(300), nullable=True)
    conservation_status = Column(String(100), nullable=True, index=True)
    family = Column(String(150), nullable=True)
    gestation_period_days = Column(String(50), nullable=True)
    social_structure = Column(String(100), nullable=True)
    offspring_per_birth = Column(String(50), nullable=True)

    # Feature Engineering columns
    size_category = Column(String(50), nullable=True)
    speed_category = Column(String(50), nullable=True)
    risk_score = Column(Float, nullable=True)
    endangered_level = Column(Integer, nullable=True)
    survival_probability = Column(Float, nullable=True)

    # Metadata
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_animal_name_lower", "name"),
        Index("idx_conservation", "conservation_status"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "color": self.color,
            "lifespan_years": self.lifespan_years,
            "diet": self.diet,
            "habitat": self.habitat,
            "predators": self.predators,
            "top_speed_kmh": self.top_speed_kmh,
            "countries_found": self.countries_found,
            "conservation_status": self.conservation_status,
            "family": self.family,
            "gestation_period_days": self.gestation_period_days,
            "social_structure": self.social_structure,
            "offspring_per_birth": self.offspring_per_birth,
            "size_category": self.size_category,
            "speed_category": self.speed_category,
            "risk_score": self.risk_score,
            "endangered_level": self.endangered_level,
            "survival_probability": self.survival_probability,
            "source_file": self.source_file,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }


class Upload(Base):
    """Upload history tracking."""
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    rows_total = Column(Integer, nullable=True)
    rows_inserted = Column(Integer, nullable=True)
    rows_duplicate = Column(Integer, nullable=True)
    rows_invalid = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)
    status = Column(String(50), default="pending")   # pending, success, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=func.now())


class PipelineLog(Base):
    """Pipeline execution logs."""
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False)
    stage = Column(String(100), nullable=True)
    level = Column(String(20), default="INFO")     # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)    # JSON string for extra data
    created_at = Column(DateTime, default=func.now())


class AnalyticsCache(Base):
    """Cache for expensive analytics queries."""
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False)
    result_json = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
