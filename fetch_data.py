"""
fetch_data.py — Bagimsiz veri cekme scripti
Uygulamadan bagimsiz olarak Dunya Bankasi verisini cekip parquet kaydeder.
"""
import sys, os, types
sys.stdout.reconfigure(encoding='utf-8')

# sbf_terminal paketini kayıt et
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if 'sbf_terminal' not in sys.modules:
    _pkg = types.ModuleType('sbf_terminal')
    _pkg.__path__ = [_this_dir]
    _pkg.__package__ = 'sbf_terminal'
    sys.modules['sbf_terminal'] = _pkg

import math
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import wbgapi as wb

from sbf_terminal.constants import INDICATORS, parquet_path

print("=" * 60)
print("Dünya Bankası Veri Çekme Başlıyor...")
print(f"Hedef: {parquet_path}")
print("=" * 60)

inds = {k: v for k, v in INDICATORS.items() if k != 'HD.HCI.OVRL'}
chunk_size = 3
all_keys = list(inds.keys())
total_chunks = math.ceil(len(all_keys) / chunk_size)
fdf_main = None

for i in range(0, len(all_keys), chunk_size):
    chunk = all_keys[i:i + chunk_size]
    chunk_num = i // chunk_size + 1
    print(f"[{chunk_num}/{total_chunks}] Çekiliyor: {[inds[k] for k in chunk]}")
    try:
        _pool = ThreadPoolExecutor(max_workers=1)
        _future = _pool.submit(wb.data.DataFrame, chunk, time=range(2000, 2026))
        try:
            cdf = _future.result(timeout=240)
        except FuturesTimeout:
            print(f"  ⚠️ Zaman aşımı! Atlandı: {chunk}")
            _pool.shutdown(wait=False)
            continue
        _pool.shutdown(wait=False)

        cdf = cdf.stack().to_frame(name='v').reset_index()
        if len(cdf.columns) == 4:
            cdf.columns = ['ISO', 'Series', 'Yıl', 'Val']
            cdf = cdf.pivot_table(index=['ISO', 'Yıl'], columns='Series', values='Val', aggfunc='first')
        else:
            cdf.columns = ['ISO', 'Yıl', 'Val']
            cdf = cdf.set_index(['ISO', 'Yıl'])
            cdf.columns = [chunk[0]]

        if fdf_main is None:
            fdf_main = cdf
        else:
            fdf_main = pd.merge(fdf_main, cdf, left_index=True, right_index=True, how='outer')
        print(f"  ✓ {len(cdf)} satır")
    except Exception as ex:
        print(f"  ✗ Hata: {ex}")

if fdf_main is None:
    print("HATA: Hiç veri çekilemedi!")
    sys.exit(1)

print("\n[Ülke metadata çekiliyor...]")
fdf_main.reset_index(inplace=True)
fdf_main['Yıl'] = fdf_main['Yıl'].astype(str).str.replace('YR', '').replace('', '0').astype(int)
fdf_main.rename(columns=inds, inplace=True)

ec = wb.economy.DataFrame()[['name', 'longitude', 'latitude', 'incomeLevel', 'region', 'aggregate']]
fdf = pd.merge(fdf_main, ec, left_on='ISO', right_index=True)
fdf = fdf[fdf['aggregate'] == False]
fdf.rename(columns={'name': 'Ülke', 'longitude': 'Lon', 'latitude': 'Lat', 'incomeLevel': 'Gelir_Grubu'}, inplace=True)
fdf = fdf.sort_values(['ISO', 'Yıl']).reset_index(drop=True)

# Sayısal dönüşüm
for col in inds.values():
    if col in fdf.columns:
        fdf[col] = pd.to_numeric(fdf[col], errors='coerce')

print(f"\n[WB verisi hazır: {len(fdf)} satır, {fdf['ISO'].nunique()} ülke]")

# Tayvan & Kuzey Kore ekle
print("\n[Tayvan & Kuzey Kore ekleniyor...]")
try:
    from extra_data import get_extra_countries_data
    extra_df = get_extra_countries_data()
    if extra_df is not None and not extra_df.empty:
        fdf = fdf[~fdf['ISO'].isin(['TWN', 'PRK'])]
        fdf = pd.concat([fdf, extra_df], ignore_index=True)
        print(f"  ✓ {len(extra_df)} satır eklendi (TWN/PRK)")
        print(f"  TWN satırları: {len(fdf[fdf['ISO']=='TWN'])}")
        print(f"  PRK satırları: {len(fdf[fdf['ISO']=='PRK'])}")
except Exception as e:
    print(f"  ✗ ExtraData hatası: {e}")

# OWID Eklentilerini Yükle
print("\n[OWID Eklentileri Yükleniyor...]")
try:
    import importlib
    import pkgutil
    import plugins
    
    for _, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
        if is_pkg or module_name == "base_plugin":
            continue
        try:
            mod = importlib.import_module(f"plugins.{module_name}")
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and attr.__name__ != "BasePlugin" and issubclass(attr, plugins.base_plugin.BasePlugin):
                    plugin_instance = attr()
                    print(f"\n[{plugin_instance.name}] Çalıştırılıyor...")
                    plugin_df = plugin_instance.fetch_data()
                    if plugin_df is not None and not plugin_df.empty:
                        # Ana DataFrame ile birleştir (ISO ve Yıl üzerinden)
                        # Önce plugin_df'teki fazla sütunları temizle ('Ülke' vs.) eğer varsa
                        merge_cols = ['ISO', 'Yıl'] + [c for c in plugin_df.columns if c not in fdf.columns and c not in ['Ülke', 'region', 'Gelir_Grubu', 'Lat', 'Lon', 'aggregate', 'country']]
                        
                        fdf = pd.merge(fdf, plugin_df[merge_cols], on=['ISO', 'Yıl'], how='left')
                        print(f"  ✓ {len(plugin_df)} satır işlendi, yeni sütunlar eklendi: {[c for c in merge_cols if c not in ['ISO', 'Yıl']]}")
                    else:
                        print(f"  ✗ Veri dönmedi.")
        except Exception as e:
            print(f"  ✗ {module_name} eklentisi yüklenirken hata: {e}")
except Exception as e:
    print(f"  ✗ Plugin sistemi hatası: {e}")

print(f"\n[Toplam: {len(fdf)} satır, {fdf['ISO'].nunique()} ülke/bölge]")
print(f"[Parquet kaydediliyor: {parquet_path}]")

fdf.to_parquet(parquet_path, engine='pyarrow', index=False)
print("✅ Kaydedildi!")
print("=" * 60)
