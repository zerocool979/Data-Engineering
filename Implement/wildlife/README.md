---

```
unzip wildlife-intelligence-pipeline.zip
cd wildlife-intelligence-pipeline
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

**Python files:**

| File | Fungsi |
|------|--------|
| `scripts/upload_handler.py` | Simpan file CSV upload ke `data/uploads/` dengan timestamp |
| `scripts/data_cleaner.py` | Hapus null, trim whitespace, konversi range angka (e.g. `"40-65"` → `52.5`) |
| `scripts/feature_engineering.py` | Tambah kolom `Size Category` & `Speed Category` |
| `scripts/pipeline_runner.py` | Orkestrasi pipeline: merge → dedup → clean → feature → save |
| `dashboard/app.py` | Streamlit UI dengan dark wildlife theme |

---

**fitur:**
- ✅ Upload CSV → append data (tidak overwrite master)
- ✅ Anti-duplikasi by `Animal`
- ✅ Data cleaning + numeric range handling
- ✅ Feature engineering: Size & Speed Category
- ✅ Search animal dengan detail card + conservation badge
- ✅ 5 chart Plotly (bar, pie, histogram)
- ✅ Summary cards (Total Animals, Habitats, Countries, Endangered)
- ✅ Download Clean Dataset button
- ✅ Pipeline logging ke `logs/pipeline.log`
- ✅ Dataset Animal_Dataset.csv sudah di-bundle sebagai master data
