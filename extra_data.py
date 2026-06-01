"""
extra_data.py — Tayvan (TWN) ve Kuzey Kore (PRK) ek veri modülü
Birincil kaynak: CIA World Factbook JSON (factbook/factbook.json, Public Domain)
Fallback/takviye: Bank of Korea (BoK) tarihsel büyüme tahminleri (PRK 1990-2020)

CIA Factbook: son 3-5 yıl için güncel veriler (SAGP-GDP, büyüme, enflasyon, işsizlik, Gini vb.)
BoK: Kuzey Kore için 1990-2020 arası büyüme serisi
"""
import re
import urllib.request
import json
import pandas as pd

# ── CIA Factbook JSON URL'leri ──────────────────────────────────────────────
FACTBOOK_URLS = {
    'TWN': 'https://raw.githubusercontent.com/factbook/factbook.json/master/east-n-southeast-asia/tw.json',
    'PRK': 'https://raw.githubusercontent.com/factbook/factbook.json/master/east-n-southeast-asia/kn.json',
}

# ── Ülke metadata ───────────────────────────────────────────────────────────
COUNTRY_META = {
    'TWN': {'Ülke': 'Taiwan',      'Lon': 120.96, 'Lat': 23.69, 'Gelir_Grubu': 'High income', 'region': 'EAS'},
    'PRK': {'Ülke': 'North Korea', 'Lon': 127.51, 'Lat': 40.33, 'Gelir_Grubu': 'Low income',  'region': 'EAS'},
}

# ── CIA alanı → uygulama sütunu eşlemesi ────────────────────────────────────
FIELD_MAP = [
    ('Real GDP (purchasing power parity)',                        'GSYİH (SAGP)',           'billion_usd'),
    ('GDP (official exchange rate)',                              'GSYİH',                  'parse_str'),
    ('Real GDP growth rate',                                     'Büyüme',                 'pct'),
    ('Real GDP per capita',                                      'Kişi Başı GSYİH (SAGP)', 'parse_str'),
    ('Inflation rate (consumer prices)',                         'Enflasyon',              'pct'),
    ('Unemployment rate',                                        'İşsizlik',               'pct'),
    ('Gini Index coefficient - distribution of family income',  'Gini',                   'num'),
    ('Public debt',                                              'Borç Oranı',             'pct'),
    ('Current account balance',                                  'Cari Denge',             'parse_str'),
    ('Exports',                                                  'İhracat',                'parse_str'),
    ('Imports',                                                  'İthalat',                'parse_str'),
]

# ── Bank of Korea: Kuzey Kore Büyüme Tahminleri (1990-2020) ────────────────
BOK_PRK_GROWTH = {
    1990: -4.3, 1991: -5.1, 1992: -7.1, 1993: -4.3, 1994: -1.2,
    1995: -4.1, 1996: -3.6, 1997: -6.5, 1998: -1.1, 1999: 6.2,
    2000: 1.3,  2001: 3.7,  2002: 1.2,  2003: 1.8,  2004: 2.2,
    2005: 3.8,  2006: -1.1, 2007: -2.3, 2008: 3.1,  2009: -0.9,
    2010: -0.5, 2011: 0.8,  2012: 1.3,  2013: 1.1,  2014: 1.0,
    2015: -1.1, 2016: 3.9,  2017: -3.5, 2018: -4.1, 2019: 0.4,
    2020: -4.5,
}


def _parse_value(text: str, fmt: str):
    """CIA Factbook metin değerini sayıya çevirir."""
    if not text:
        return None
    text = re.sub(r'<[^>]+>', '', text).strip()
    try:
        if fmt == 'pct':
            m = re.search(r'-?\d+\.?\d*', text)
            return float(m.group()) if m else None

        elif fmt == 'num':
            m = re.search(r'\d+\.?\d*', text)
            return float(m.group()) if m else None

        elif fmt in ('billion_usd', 'parse_str'):
            m = re.search(r'\$?([\d,.]+)\s*(trillion|billion|million)?', text, re.I)
            if not m:
                return None
            val = float(m.group(1).replace(',', ''))
            unit = (m.group(2) or '').lower()
            if unit == 'trillion':
                val *= 1e12
            elif unit == 'billion':
                val *= 1e9
            elif unit == 'million':
                val *= 1e6
            return val
    except Exception:
        return None


def _fetch_factbook(iso: str) -> dict:
    """CIA Factbook JSON'ı indirir."""
    url = FACTBOOK_URLS.get(iso)
    if not url:
        return {}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f'[CIA Factbook] {iso} indirilemedi: {e}')
        return {}


def _extract_cia_data(iso: str) -> pd.DataFrame:
    """CIA Factbook'tan ülke verisi çıkarır."""
    data = _fetch_factbook(iso)
    if not data:
        return pd.DataFrame()

    econ = data.get('Economy', {})
    year_data = {}

    for cia_field, col_name, fmt in FIELD_MAP:
        if cia_field not in econ:
            continue
        field_dict = econ[cia_field]
        if not isinstance(field_dict, dict):
            continue

        for key, val_obj in field_dict.items():
            yr_match = re.search(r'(20\d\d|19\d\d)', key)
            if not yr_match:
                continue
            yr = int(yr_match.group(1))
            text = val_obj.get('text', '') if isinstance(val_obj, dict) else str(val_obj)
            num = _parse_value(text, fmt)
            if num is None:
                continue
            if yr not in year_data:
                year_data[yr] = {'ISO': iso, 'Yıl': yr}
            year_data[yr][col_name] = num

    if not year_data:
        return pd.DataFrame()

    df = pd.DataFrame(list(year_data.values()))
    meta = COUNTRY_META.get(iso, {})
    for k, v in meta.items():
        df[k] = v
    df['aggregate'] = None
    return df


def get_taiwan_data() -> pd.DataFrame:
    """Tayvan için CIA Factbook verisi."""
    print('[CIA Factbook] TWN verisi çekiliyor...')
    df = _extract_cia_data('TWN')
    if not df.empty:
        print(f'  ✓ TWN: {len(df)} yıl, {[c for c in df.columns if c not in COUNTRY_META["TWN"]]}')
    else:
        print('  ✗ TWN için veri alınamadı.')
    return df


def get_nk_data() -> pd.DataFrame:
    """Kuzey Kore için CIA Factbook + Bank of Korea verisi."""
    print('[CIA Factbook] PRK verisi çekiliyor...')
    df_cia = _extract_cia_data('PRK')

    # BoK tarihsel büyüme serisini ekle (1990-2020)
    meta = COUNTRY_META['PRK']
    bok_rows = []
    cia_years = set(df_cia['Yıl'].tolist()) if not df_cia.empty else set()

    for yr, growth in BOK_PRK_GROWTH.items():
        row = {'ISO': 'PRK', 'Yıl': yr, 'Büyüme': growth, 'aggregate': None}
        row.update(meta)
        # CIA verisi varsa büyümeyi üzerine yaz (CIA daha güncel)
        if yr in cia_years:
            continue
        bok_rows.append(row)

    df_bok = pd.DataFrame(bok_rows)

    # Birleştir: CIA (güncel) + BoK (tarihsel)
    if not df_cia.empty and not df_bok.empty:
        df = pd.concat([df_cia, df_bok], ignore_index=True)
    elif not df_cia.empty:
        df = df_cia
    else:
        df = df_bok

    df = df.sort_values('Yıl').reset_index(drop=True)
    print(f'  ✓ PRK: {len(df)} yıl (CIA: {len(df_cia)}, BoK: {len(df_bok)})')
    return df


def get_extra_countries_data() -> pd.DataFrame:
    """Tayvan ve Kuzey Kore verilerini birleştirir."""
    dfs = []
    df_twn = get_taiwan_data()
    if not df_twn.empty:
        dfs.append(df_twn)

    df_prk = get_nk_data()
    if not df_prk.empty:
        dfs.append(df_prk)

    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    df = get_extra_countries_data()
    print('\n=== SONUÇ ===')
    print(f'Toplam: {len(df)} satır')
    print(f'TWN: {len(df[df["ISO"]=="TWN"])} yıl')
    print(f'PRK: {len(df[df["ISO"]=="PRK"])} yıl')
    print('\nTWN (son 5 yıl):')
    print(df[df['ISO']=='TWN'].tail(5).to_string())
    print('\nPRK (ilk 5 + son 5):')
    prk = df[df['ISO']=='PRK']
    print(pd.concat([prk.head(3), prk.tail(3)]).to_string())
