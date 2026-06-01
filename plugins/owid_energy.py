import pandas as pd
from .base_plugin import BasePlugin

class OWIDEnergyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "OWID Energy Data"

    def fetch_data(self) -> pd.DataFrame:
        url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
        print(f"[{self.name}] İndiriliyor: {url}")
        df = pd.read_csv(url)
        
        # Sadece ISO kodu olan (ülkeler) ve gerekli sütunları al
        df = df[df['iso_code'].notna()]
        
        cols_to_keep = {
            'iso_code': 'ISO',
            'year': 'Yıl',
            'energy_per_capita': 'Kişi Başı Enerji (kWh)',
            'fossil_share_elec': 'Fosil Yakıt Payı (%)',
            'renewables_share_elec': 'Yenilenebilir Payı (%)'
        }
        
        # Sadece bizim listemizde olan mevcut sütunları al
        existing_cols = [c for c in cols_to_keep.keys() if c in df.columns]
        df = df[existing_cols].rename(columns=cols_to_keep)
        
        # Filtreleme (Çok eski yılları at, parquet dosyamız 2000'den başlıyor ama merge outer olacak,
        # istersen hepsini tutabiliriz. Şimdilik > 1980 olanları alalım).
        df = df[df['Yıl'] >= 1990].copy()
        
        return df

    def get_metadata(self) -> dict:
        return {
            'Kişi Başı Enerji (kWh)': {
                'tanim': 'Kişi başı birincil enerji tüketimi (kilovat saat).',
                'birim': 'kWh',
                'metodoloji': 'Our World in Data (Energy Data)'
            },
            'Fosil Yakıt Payı (%)': {
                'tanim': 'Toplam elektrik üretiminde fosil yakıtların (kömür, petrol, gaz) yüzdesi.',
                'birim': '%',
                'metodoloji': 'Our World in Data (Energy Data)'
            },
            'Yenilenebilir Payı (%)': {
                'tanim': 'Toplam elektrik üretiminde yenilenebilir kaynakların (hidro, güneş, rüzgar) yüzdesi.',
                'birim': '%',
                'metodoloji': 'Our World in Data (Energy Data)'
            }
        }
