"""
data_engine.py — Veri motoru ve sosyal gösterge yükleyicileri
SmartDataEngine: Parquet/CSV hibrit veri yönetimi
"""
import os
import pandas as pd
import numpy as np

from sbf_terminal.constants import social_csv_path


# ── Sosyal Gösterge Yükleyicileri ─────────────────────────────────────────────
def load_social_indicators():
    """Uygulama klasöründeki social_indicators.csv dosyasını okur."""
    if not os.path.exists(social_csv_path):
        print(f"social_indicators.csv bulunamadi: {social_csv_path}")
        return pd.DataFrame()
    try:
        sdf = pd.read_csv(social_csv_path, encoding='utf-8')
        sdf.columns = [c.strip() for c in sdf.columns]
        required = {'ISO', 'Year'}
        if not required.issubset(set(sdf.columns)):
            print("social_indicators.csv: 'ISO' ve 'Year' sutunlari zorunludur.")
            return pd.DataFrame()
        sdf['Year'] = pd.to_numeric(sdf['Year'], errors='coerce').astype('Int64')
        for col in sdf.columns:
            if col not in ['ISO', 'Year']:
                sdf[col] = pd.to_numeric(sdf[col], errors='coerce')
        return sdf
    except Exception as e:
        print(f"social_indicators.csv okuma hatasi: {e}")
        return pd.DataFrame()


def merge_social_indicators(df):
    """Ana dataframe (WB) ile yerel CSV'yi ISO+Yıl üzerinden birleştirir."""
    sdf = load_social_indicators()
    if sdf.empty:
        return df
    try:
        sdf = sdf.rename(columns={'Year': 'Yıl'})
        sdf['Yıl'] = sdf['Yıl'].astype(int)
        merged = pd.merge(df, sdf, on=['ISO', 'Yıl'], how='left', suffixes=('', '_csv'))
        numeric_cols = [c for c in sdf.columns if c not in ['ISO', 'Yıl']]
        for col in numeric_cols:
            if col + '_csv' in merged.columns:
                if col in merged.columns:
                    merged[col] = merged[col].combine_first(merged[col + '_csv'])
                else:
                    merged[col] = merged[col + '_csv']
                merged.drop(columns=[col + '_csv'], inplace=True)
        return merged
    except Exception as e:
        print(f"⚠️ Sosyal gösterge birleştirme hatası: {e}")
        return df


# ── SmartDataEngine ────────────────────────────────────────────────────────────
class SmartDataEngine:
    """
    Hibrit Kaynaklı Makroekonomik Veri Terminali — Akıllı Güncelleme Motoru
    Kaynak hiyerarşisi: UN_Manual > WB > IMF
    """
    MANUAL_TAG = 'UN_Manual'
    WB_TAG     = 'WB'
    IMF_TAG    = 'IMF'
    KEY_COLS   = ('ISO', 'Yıl')
    META_COLS  = {'ISO', 'Yıl', 'Ülke', 'Lon', 'Lat', 'Gelir_Grubu', 'region', 'aggregate',
                  'incomeLevel', 'name', 'GSYİH_Sıra', 'v', 'Series', 'Val'}

    def __init__(self, parquet_path, csv_path):
        self.parquet_path = parquet_path
        self.csv_path     = csv_path
        self._df  = None
        self._src = None

    # ── Yükleme ───────────────────────────────────────────────────────────────
    def load(self):
        """Parquet'ten WB verisini yükle ve kaynak matrisini hazırla."""
        if not os.path.exists(self.parquet_path):
            return pd.DataFrame()
        self._df = pd.read_parquet(self.parquet_path, engine='pyarrow')
        num_cols = [c for c in self._df.columns if c not in self.META_COLS]
        self._src = pd.DataFrame(
            data={c: self.WB_TAG for c in num_cols},
            index=self._df.index
        )
        self._mark_manual_sources()
        return self._df

    def _mark_manual_sources(self):
        """social_indicators.csv kökenli sütunları UN_Manual olarak işaretle."""
        if not os.path.exists(self.csv_path) or self._src is None:
            return
        try:
            sdf = pd.read_csv(self.csv_path, encoding='utf-8')
            sdf.columns = [c.strip() for c in sdf.columns]
            manual_cols = [c for c in sdf.columns if c not in ('ISO', 'Year')]
            for col in manual_cols:
                if col in self._src.columns:
                    self._src[col] = self.MANUAL_TAG
        except Exception as e:
            print(f"[SmartDB] Kaynak işaretleme hatası: {e}")

    # ── Boşluk Taraması ───────────────────────────────────────────────────────
    def scan_gaps(self, indicators=None):
        """NaN hücreleri tara. Döndür: {sütun: nan_sayısı}"""
        if self._df is None:
            return {}
        targets = indicators or [c for c in self._df.columns if c not in self.META_COLS]
        return {c: int(self._df[c].isna().sum())
                for c in targets if c in self._df.columns and self._df[c].isna().any()}

    # ── Korumalı Upsert ───────────────────────────────────────────────────────
    def upsert_api(self, api_df, source_tag):
        """
        API verisini koruma şalıdırıyla entegre eder.
        UN_Manual etiketli hücreler hiçbir koşulda güncellenmez.
        """
        if self._df is None or api_df is None or api_df.empty:
            return
        key_list = list(self.KEY_COLS)
        api_cols = [c for c in api_df.columns if c not in self.KEY_COLS]

        base   = self._df[key_list].reset_index()
        merged = pd.merge(base, api_df, on=key_list, how='left').set_index('index')

        for col in api_cols:
            if col not in merged.columns:
                continue
            api_vals = merged[col]
            if self._src is not None and col in self._src.columns:
                protected = (self._src[col] == self.MANUAL_TAG)
            else:
                protected = pd.Series(False, index=self._df.index)
            update_mask = ~protected & api_vals.notna()
            if col not in self._df.columns:
                self._df[col] = np.nan
                if self._src is not None:
                    self._src[col] = source_tag
            self._df.loc[update_mask, col] = api_vals[update_mask].values
            if self._src is not None:
                self._src.loc[update_mask, col] = source_tag

        gaps = self.scan_gaps(api_cols)
        if gaps:
            print(f"[SmartDB] {source_tag} sonrası kalan boşluklar: " +
                  ", ".join(f"{k}={v}" for k, v in gaps.items()))

    # ── Yedek + Kaydet ────────────────────────────────────────────────────────
    def backup_and_save(self):
        """Kaydetmeden önce .bak yedeği oluşturur, ardından parquet kaydeder."""
        if self._df is None:
            return
        import shutil
        bak = self.parquet_path + '.bak'
        if os.path.exists(self.parquet_path):
            shutil.copy2(self.parquet_path, bak)
            print(f"[SmartDB] Yedek oluşturuldu → {bak}")
        self._df.to_parquet(self.parquet_path, engine='pyarrow', index=False)
        print(f"[SmartDB] Kaydedildi → {self.parquet_path}")

    @property
    def df(self):
        return self._df
