"""
backend/routes/upload.py - File Upload & Pipeline Trigger API
Wildlife Intelligence Monitoring System
"""
import shutil
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.database.connection import get_session
from backend.database.models import Upload

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", summary="Upload CSV and run ETL pipeline")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a wildlife CSV file.
    Automatically runs: Validate → Clean → Feature Engineer → Load to DB.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Save file
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Read and run pipeline
    try:
        df = pd.read_csv(dest)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read CSV: {e}")

    from pipeline.pipeline_runner import PipelineRunner
    runner = PipelineRunner()
    result = runner.run(df, source_file=file.filename)

    if result["status"] == "failed":
        raise HTTPException(status_code=422, detail=result.get("error", "Pipeline failed"))

    return result


@router.get("/history", summary="Get upload history")
def upload_history(db=None):
    """Return history of all uploaded files and their pipeline results."""
    session = get_session()
    try:
        uploads = session.query(Upload).order_by(Upload.uploaded_at.desc()).limit(50).all()
        return [
            {
                "id": u.id,
                "filename": u.filename,
                "rows_total": u.rows_total,
                "rows_inserted": u.rows_inserted,
                "rows_duplicate": u.rows_duplicate,
                "quality_score": u.quality_score,
                "status": u.status,
                "uploaded_at": str(u.uploaded_at),
            }
            for u in uploads
        ]
    finally:
        session.close()
