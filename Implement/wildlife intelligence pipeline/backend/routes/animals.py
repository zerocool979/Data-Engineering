"""
backend/routes/animals.py - Animals CRUD REST API
Wildlife Intelligence Monitoring System
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import Animal

router = APIRouter()


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class AnimalCreate(BaseModel):
    name: str
    height_cm: Optional[str] = None
    weight_kg: Optional[str] = None
    color: Optional[str] = None
    lifespan_years: Optional[str] = None
    diet: Optional[str] = None
    habitat: Optional[str] = None
    predators: Optional[str] = None
    top_speed_kmh: Optional[float] = None
    countries_found: Optional[str] = None
    conservation_status: Optional[str] = "Unknown"
    family: Optional[str] = None
    social_structure: Optional[str] = None
    offspring_per_birth: Optional[str] = None


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    height_cm: Optional[str] = None
    weight_kg: Optional[str] = None
    color: Optional[str] = None
    lifespan_years: Optional[str] = None
    diet: Optional[str] = None
    habitat: Optional[str] = None
    predators: Optional[str] = None
    top_speed_kmh: Optional[float] = None
    countries_found: Optional[str] = None
    conservation_status: Optional[str] = None
    family: Optional[str] = None
    social_structure: Optional[str] = None
    offspring_per_birth: Optional[str] = None


# ── CRUD Endpoints ────────────────────────────────────────────────────────────

@router.get("/", summary="List all animals")
def list_animals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    animals = db.query(Animal).filter(Animal.is_active == True).offset(skip).limit(limit).all()
    return {"total": len(animals), "animals": [a.to_dict() for a in animals]}


@router.get("/{animal_id}", summary="Get animal by ID")
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(Animal).filter(Animal.id == animal_id, Animal.is_active == True).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal.to_dict()


@router.post("/", summary="Create new animal", status_code=201)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db)):
    # Check duplicate name
    existing = db.query(Animal).filter(
        Animal.name.ilike(payload.name), Animal.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Animal '{payload.name}' already exists.")

    from pipeline.feature_engineering import FeatureEngineer
    import pandas as pd

    animal = Animal(**payload.model_dump(), source_file="manual_entry")

    # Run feature engineering on single row
    fe = FeatureEngineer()
    row_df = pd.DataFrame([payload.model_dump()])
    row_df["top_speed_kmh"] = payload.top_speed_kmh or 0
    row_df = fe.engineer(row_df)
    animal.speed_category = row_df["speed_category"].iloc[0]
    animal.size_category = row_df["size_category"].iloc[0]
    animal.risk_score = row_df["risk_score"].iloc[0]
    animal.endangered_level = int(row_df["endangered_level"].iloc[0])
    animal.survival_probability = row_df["survival_probability"].iloc[0]

    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal.to_dict()


@router.put("/{animal_id}", summary="Update animal")
def update_animal(animal_id: int, payload: AnimalUpdate, db: Session = Depends(get_db)):
    animal = db.query(Animal).filter(Animal.id == animal_id, Animal.is_active == True).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(animal, field, value)

    db.commit()
    db.refresh(animal)
    return animal.to_dict()


@router.delete("/{animal_id}", summary="Delete animal (soft delete)")
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    animal.is_active = False
    db.commit()
    return {"message": f"Animal ID {animal_id} deleted successfully."}
