import pandas as pd
df = pd.read_parquet('C:/Users/pc/Desktop/2antigravity/macro_data_25y.parquet')
print('Columns:', df.columns.tolist())
twn = df[df['ISO']=='TWN']
prk = df[df['ISO']=='PRK']
print()
print('=== TAYVAN ===')
print('Satir sayisi:', len(twn))
print(twn[['ISO','Yil','Ulke','Lon','Lat','GSYiH']].head(3).to_string() if 'Ulke' in df.columns else twn.head(3).to_string())
print()
print('=== KUZEY KORE ===')
print('Satir sayisi:', len(prk))
print(prk.head(3).to_string())
