"""
run.py - Application startup script
Wildlife Intelligence Monitoring System

Usage:
    python run.py           # Load data + launch dashboard
    python run.py --api     # Also start FastAPI server
"""
import sys
import subprocess
from pathlib import Path

# Project root
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def load_initial_data():
    """Run ETL on all CSVs in master + uploads folders."""
    print("🌿 Wildlife Intelligence Monitoring System")
    print("=" * 50)
    print("📦 Loading initial datasets...")

    from pipeline.pipeline_runner import run_initial_load
    results = run_initial_load()

    total_inserted = sum(r.get("rows_inserted", 0) for r in results if r.get("status") == "success")
    print(f"✅ Data load complete. Total animals inserted: {total_inserted}")
    for r in results:
        status = "✅" if r["status"] == "success" else "❌"
        print(f"  {status} {r.get('source', '?')} — inserted: {r.get('rows_inserted', 0)}, quality: {r.get('quality_score', 0)}%")


def launch_dashboard():
    print("\n🚀 Launching Streamlit Dashboard...")
    print("   Open: http://localhost:8501\n")
    subprocess.run(
        ["streamlit", "run", str(ROOT / "dashboard" / "app.py"),
         "--server.port", "8501",
         "--server.headless", "true",
         "--theme.base", "dark"],
        cwd=str(ROOT),
    )


def launch_api():
    print("\n🔌 Launching FastAPI Backend...")
    print("   Docs: http://localhost:8000/docs\n")
    subprocess.Popen(
        ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    load_initial_data()
    if "--api" in sys.argv:
        launch_api()
    launch_dashboard()
