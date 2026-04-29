# Teen Mental Health Pipeline

---

**Run:**

```bash
cd file
tar -xzf teen-mental-health-pipeline-v2.tar.gz
cd teen-mental-health-pipeline
pip install -r requirements.txt
python scripts/run_pipeline.py
streamlit run dashboard/app.py
```

---

**Python files:**

| File                     | Fungsi                                                                            |
| ------------------------ | --------------------------------------------------------------------------------- |
| `run_pipeline.py`        | Menjalankan pipeline utama: ingestion → validation → cleaning → feature → scoring |
| `scheduler.py`           | Menjadwalkan pipeline berjalan otomatis harian                                    |
| `alert_system.py`        | Mengirim notifikasi jika risk threshold terlampaui                                |
| `data_versioning.py`     | Menyimpan snapshot data dengan checksum versioning                                |
| `data_quality_report.py` | Membuat laporan kualitas data dalam format HTML                                   |
| `app.py`                 | Dashboard Streamlit untuk visualisasi hasil pipeline                              |

---

**fitur:**

* ✅ Automated Data Pipeline (end-to-end processing)
* ✅ Scheduler harian untuk pipeline automation
* ✅ Retry & logging pada proses penting
* ✅ Data Quality Report dalam bentuk HTML
* ✅ Data Versioning berbasis checksum
* ✅ Risk Alert System dengan threshold detection
* ✅ Model comparison & prediction pipeline
* ✅ Interactive dashboard berbasis Streamlit
* ✅ Monitoring pipeline melalui logs
* ✅ Data snapshot rollback support

---
