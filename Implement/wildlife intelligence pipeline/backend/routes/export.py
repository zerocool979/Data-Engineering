"""
backend/routes/export.py - Data Export API
Wildlife Intelligence Monitoring System
"""
import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response

from backend.database.connection import get_session
from backend.database.models import Animal
from pipeline.exporter import DataExporter

router = APIRouter()
exporter = DataExporter()

MIME_TYPES = {
    "csv": "text/csv",
    "json": "application/json",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "parquet": "application/octet-stream",
    "sql": "text/plain",
}


def _get_df(conservation_filter: str = None) -> pd.DataFrame:
    session = get_session()
    try:
        q = session.query(Animal).filter(Animal.is_active == True)
        if conservation_filter and conservation_filter != "All":
            q = q.filter(Animal.conservation_status == conservation_filter)
        animals = q.all()
        return pd.DataFrame([a.to_dict() for a in animals])
    finally:
        session.close()


@router.get("/{format}", summary="Export data in specified format")
def export_data(
    format: str,
    conservation: str = Query("All", description="Filter by conservation status"),
):
    """
    Export wildlife data. Supported formats: csv, json, xlsx, parquet, sql
    """
    if format not in MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Use: {list(MIME_TYPES.keys())}")

    df = _get_df(conservation_filter=conservation)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found.")

    export_fns = {
        "csv": exporter.to_csv,
        "json": exporter.to_json,
        "xlsx": exporter.to_excel,
        "parquet": exporter.to_parquet,
        "sql": exporter.to_sql_dump,
    }

    data = export_fns[format](df)
    filename = f"wildlife_data.{format}"

    return Response(
        content=data,
        media_type=MIME_TYPES[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
