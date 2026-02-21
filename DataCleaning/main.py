import pandas as pd
import numpy as np

# ===============================
# 1. LOAD DATA
# ===============================
file_path = input("Masukkan path file (csv/json): ")

if file_path.endswith(".csv"):
    df = pd.read_csv(file_path)
elif file_path.endswith(".json"):
    df = pd.read_json(file_path)
else:
    print("Format tidak didukung")
    exit()

print("\n=== INFO AWAL DATA ===")
print(df.info())
print(df.head())

# Backup data asli
df_original = df.copy()

# ===============================
# 2. HANDLE MISSING VALUES
# ===============================
print("\n=== CEK MISSING VALUE ===")
print(df.isnull().sum())

# Hapus baris kosong total
df.dropna(how='all', inplace=True)

# Isi numeric null dengan median
numeric_cols = df.select_dtypes(include=np.number).columns
for col in numeric_cols:
    df[col].fillna(df[col].median(), inplace=True)

# Isi text null dengan "unknown"
text_cols = df.select_dtypes(include="object").columns
for col in text_cols:
    df[col].fillna("unknown", inplace=True)

# ===============================
# 3. HAPUS DUPLIKAT
# ===============================
print("\nDuplikat sebelum:", df.duplicated().sum())
df.drop_duplicates(inplace=True)
print("Duplikat sesudah:", df.duplicated().sum())

# ===============================
# 4. BERSIHKAN FORMAT ANGKA (contoh harga)
# ===============================
for col in df.columns:
    if "harga" in col.lower() or "price" in col.lower():
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("Rp", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ===============================
# 5. STANDARISASI TEKS
# ===============================
for col in text_cols:
    df[col] = df[col].astype(str).str.lower().str.strip()

# ===============================
# 6. HANDLE OUTLIER (IQR METHOD)
# ===============================
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]

# ===============================
# 7. KONVERSI TANGGAL
# ===============================
for col in df.columns:
    if "date" in col.lower() or "tanggal" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ===============================
# 8. FINAL CHECK
# ===============================
print("\n=== INFO SETELAH CLEANING ===")
print(df.info())
print(df.head())

# ===============================
# 9. EXPORT DATA BERSIH
# ===============================
output_file = "cleaned_data.csv"
df.to_csv(output_file, index=False)

print(f"\n✅ Data cleaning selesai.")
print(f"File tersimpan sebagai: {output_file}")
