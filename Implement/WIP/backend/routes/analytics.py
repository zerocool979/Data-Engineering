"""
backend/routes/analytics.py - Analytics Endpoints
Wildlife Intelligence Monitoring System
"""
from collections import Counter
from fastapi import APIRouter
from backend.database.connection import get_session
from backend.database.models import Animal

router = APIRouter()


def _get_animals_df():
    """Fetch all active animals as a pandas DataFrame."""
    import pandas as pd
    session = get_session()
    try:
        animals = session.query(Animal).filter(Animal.is_active == True).all()
        return pd.DataFrame([a.to_dict() for a in animals])
    finally:
        session.close()


@router.get("/summary", summary="Dashboard summary KPIs")
def get_summary():
    """Return top-level KPIs for the dashboard."""
    session = get_session()
    try:
        total = session.query(Animal).filter(Animal.is_active == True).count()
        endangered = session.query(Animal).filter(
            Animal.is_active == True,
            Animal.conservation_status.in_(["Endangered", "Critically Endangered"])
        ).count()
        habitats = session.query(Animal.habitat).filter(Animal.is_active == True).distinct().count()
        countries_raw = session.query(Animal.countries_found).filter(Animal.is_active == True).all()
        countries = set()
        for (c,) in countries_raw:
            if c and c != "Unknown":
                for cc in str(c).split(","):
                    countries.add(cc.strip())

        return {
            "total_animals": total,
            "endangered_species": endangered,
            "total_habitats": habitats,
            "countries_covered": len(countries),
        }
    finally:
        session.close()


@router.get("/conservation", summary="Conservation status distribution")
def conservation_distribution():
    """Count animals by conservation status."""
    session = get_session()
    try:
        results = session.query(Animal.conservation_status, Animal.id).filter(Animal.is_active == True).all()
        counter = Counter(r[0] or "Unknown" for r in results)
        return [{"status": k, "count": v} for k, v in sorted(counter.items(), key=lambda x: -x[1])]
    finally:
        session.close()


@router.get("/habitat", summary="Habitat distribution")
def habitat_distribution():
    """Top habitats by animal count."""
    session = get_session()
    try:
        results = session.query(Animal.habitat).filter(Animal.is_active == True).all()
        counter = Counter()
        for (h,) in results:
            if h and h != "Unknown":
                for hab in str(h).split(","):
                    counter[hab.strip()] += 1
        top = counter.most_common(15)
        return [{"habitat": k, "count": v} for k, v in top]
    finally:
        session.close()


@router.get("/diet", summary="Diet type distribution")
def diet_distribution():
    session = get_session()
    try:
        results = session.query(Animal.diet).filter(Animal.is_active == True).all()
        counter = Counter(r[0] or "Unknown" for r in results)
        return [{"diet": k, "count": v} for k, v in sorted(counter.items(), key=lambda x: -x[1])]
    finally:
        session.close()


@router.get("/speed", summary="Speed distribution")
def speed_distribution():
    """Return speed data and categories."""
    session = get_session()
    try:
        results = session.query(Animal.name, Animal.top_speed_kmh, Animal.speed_category).filter(
            Animal.is_active == True, Animal.top_speed_kmh > 0
        ).order_by(Animal.top_speed_kmh.desc()).limit(20).all()
        return [{"name": r[0], "speed": r[1], "category": r[2]} for r in results]
    finally:
        session.close()


@router.get("/risk", summary="Top risk-score animals")
def top_risk():
    """Return top 15 highest-risk animals."""
    session = get_session()
    try:
        results = session.query(
            Animal.name, Animal.risk_score, Animal.conservation_status, Animal.survival_probability
        ).filter(Animal.is_active == True).order_by(Animal.risk_score.desc()).limit(15).all()
        return [
            {"name": r[0], "risk_score": r[1], "status": r[2], "survival": r[3]}
            for r in results
        ]
    finally:
        session.close()


@router.get("/size", summary="Size category distribution")
def size_distribution():
    session = get_session()
    try:
        results = session.query(Animal.size_category).filter(Animal.is_active == True).all()
        counter = Counter(r[0] or "Unknown" for r in results)
        return [{"size": k, "count": v} for k, v in sorted(counter.items(), key=lambda x: -x[1])]
    finally:
        session.close()


@router.get("/countries", summary="Country distribution")
def country_distribution():
    session = get_session()
    try:
        results = session.query(Animal.countries_found).filter(Animal.is_active == True).all()
        counter = Counter()
        for (c,) in results:
            if c and c != "Unknown":
                for cc in str(c).split(","):
                    cc = cc.strip()
                    if cc:
                        counter[cc] += 1
        top = counter.most_common(20)
        return [{"country": k, "count": v} for k, v in top]
    finally:
        session.close()
