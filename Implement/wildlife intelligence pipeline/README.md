# WILDLIFE INTELLIGENCE PIPELINE

> Automated Data Engineering System for Wildlife Dataset Management

## Run

```bash
pip install -r requirements.txt
chmod -R 755 data
streamlit run dashboard/app.py
```

---

## Feature Engineering

- Upload CSV → append data (tidak overwrite master)
- Anti-duplikasi by `Animal`
- Data cleaning + numeric range handling
- Feature engineering: Size & Speed Category
- Search animal dengan detail card + conservation badge
- 5 chart Plotly (bar, pie, histogram)
- Summary cards (Total Animals, Habitats, Countries, Endangered)
- Download Clean Dataset button
- Pipeline logging ke `logs/pipeline.log`
- Dataset Animal_Dataset.csv sudah di-bundle sebagai master data

### Size Category (based on Weight kg)
| Category | Weight |
|----------|--------|
| Small    | < 10 kg |
| Medium   | 10 – 100 kg |
| Large    | > 100 kg |

### Speed Category (based on Top Speed km/h)
| Category | Speed |
|----------|-------|
| Slow     | < 30 km/h |
| Medium   | 30 – 60 km/h |
| Fast     | > 60 km/h |
