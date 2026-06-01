import sys
import pandas as pd
import wbgapi as wb
import os

parquet_path = r"c:\Users\pc\Desktop\2antigravity\macro_data_25y.parquet"
df = pd.read_parquet(parquet_path)

missing_inds = {
    'NE.CON.GOVT.ZS': 'Kamu Harcamaları',
    'MS.MIL.XPND.GD.ZS': 'Savunma Harcamaları',
    'GC.TAX.TOTL.GD.ZS': 'Vergi Gelirleri'
}
keys = list(missing_inds.keys())
print("Fetching from World Bank API:", keys)

try:
    cdf = wb.data.DataFrame(keys, time=range(2000, 2026))
except Exception as e:
    print("Error fetching:", e)
    sys.exit(1)

cdf = cdf.stack().to_frame(name='v').reset_index()
cdf.columns = ['ISO', 'Series', 'Yıl', 'Val']
cdf = cdf.pivot_table(index=['ISO', 'Yıl'], columns='Series', values='Val', aggfunc='first')
cdf.rename(columns=missing_inds, inplace=True)
cdf.reset_index(inplace=True)
cdf['Yıl'] = cdf['Yıl'].astype(str).str.replace('YR', '').replace('', '0').astype(int)

for col in missing_inds.values():
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

df = pd.merge(df, cdf, on=['ISO', 'Yıl'], how='left')

for col in missing_inds.values():
    if col in df.columns:
        print(f"{col} non-null: {df[col].notna().sum()}")

bak_path = parquet_path + ".bak_new"
if os.path.exists(bak_path):
    os.remove(bak_path)
if os.path.exists(parquet_path):
    os.rename(parquet_path, bak_path)

df.to_parquet(parquet_path, engine='pyarrow', index=False)
print("Done saving!")
