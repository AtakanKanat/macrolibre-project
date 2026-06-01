import pandas as pd

df = pd.read_parquet(r"c:\Users\pc\Desktop\2antigravity\macro_data_25y.parquet")

print("Checking 'Harcamaları':")
for col in df.columns:
    if 'Harcama' in col or 'Savunma' in col or 'Kamu' in col:
        print(f"Column found: '{col}' -> nulls: {df[col].isna().sum()}")

print("All columns:")
print(list(df.columns))
