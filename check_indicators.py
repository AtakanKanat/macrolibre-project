import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

df = pd.read_parquet('C:/Users/pc/Desktop/2antigravity/macro_data_25y.parquet')

for iso in ['TWN', 'PRK']:
    sub = df[df['ISO'] == iso]
    print(f'\n{"="*60}')
    print(f'{iso} — toplam {len(sub)} satır, yıllar: {sorted(sub["Yıl"].unique())}')
    print(f'{"="*60}')
    
    # Her sütun için kaç geçerli satır var
    skip = ['ISO', 'Yıl', 'Ülke', 'Lon', 'Lat', 'Gelir_Grubu', 'region', 'aggregate']
    results = []
    for col in df.columns:
        if col in skip:
            continue
        n_valid = sub[col].notna().sum()
        if n_valid > 0:
            sample = sub[sub[col].notna()][col].iloc[-1]  # en son geçerli değer
            yil = sub[sub[col].notna()]['Yıl'].iloc[-1]
            results.append((col, n_valid, yil, sample))
    
    print(f'\n✅ VERİ OLAN ({len(results)} gösterge):')
    for col, n, yil, val in sorted(results, key=lambda x: -x[1]):
        print(f'   {col:<35} {n:>3} yıl   son: {yil} = {val:.2f}')
    
    # Hiç verisi olmayanlar
    no_data = [col for col in df.columns if col not in skip and sub[col].notna().sum() == 0]
    print(f'\n❌ HİÇ VERİSİ OLMAYANLAR ({len(no_data)} gösterge):')
    for col in no_data:
        print(f'   {col}')
