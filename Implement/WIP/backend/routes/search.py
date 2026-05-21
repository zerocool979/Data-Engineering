"""
backend/routes/search.py - Search & Filter API
Wildlife Intelligence Monitoring System
"""
from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy import or_

from backend.database.connection import get_session
from backend.database.models import Animal

router = APIRouter()


@router.get("/", summary="Search animals with filters")
def search_animals(
    q: Optional[str] = Query(None, description="Search term (name, habitat, country)"),
    habitat: Optional[str] = Query(None),
    conservation_status: Optional[str] = Query(None),
    diet: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """
    Search animals by name, habitat, country, conservation status, or diet.
    All filters are combined with AND logic.
    """
    session = get_session()
    try:
        query = session.query(Animal).filter(Animal.is_active == True)

        if q:
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    Animal.name.ilike(search_term),
                    Animal.habitat.ilike(search_term),
                    Animal.countries_found.ilike(search_term),
                    Animal.color.ilike(search_term),
                )
            )

        if habitat:
            query = query.filter(Animal.habitat.ilike(f"%{habitat}%"))

        if conservation_status:
            query = query.filter(Animal.conservation_status.ilike(f"%{conservation_status}%"))

        if diet:
            query = query.filter(Animal.diet.ilike(f"%{diet}%"))

        results = query.limit(limit).all()
        return {
            "total": len(results),
            "results": [a.to_dict() for a in results],
        }
    finally:
        session.close()
