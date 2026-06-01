import pandas as pd
from .base_plugin import BasePlugin

class OWIDCO2Plugin(BasePlugin):
    @property
    def name(self) -> str:
        return "OWID CO2 Data"

    def fetch_data(self) -> pd.DataFrame:
        url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
        print(f"[{self.name}] İndiriliyor: {url}")
        df = pd.read_csv(url)
        
        df = df[df['iso_code'].notna()]
        
        cols_to_keep = {
            'iso_code': 'ISO',
            'year': 'Yıl',
            'co2': 'Karbon (Milyon Ton)',
            'co2_per_capita': 'Kişi Başı Karbon (Ton)'
        }
        
        existing_cols = [c for c in cols_to_keep.keys() if c in df.columns]
        df = df[existing_cols].rename(columns=cols_to_keep)
        
        df = df[df['Yıl'] >= 1990].copy()
        
        return df

    def get_metadata(self) -> dict:
        return {
            'Karbon (Milyon Ton)': {
                'tanim': 'Fosil yakıt kullanımı ve sanayi süreçlerinden kaynaklanan yıllık toplam CO2 emisyonu.',
                'birim': 'Milyon Ton',
                'metodoloji': 'Our World in Data (CO2 Data)'
            },
            'Kişi Başı Karbon (Ton)': {
                'tanim': 'Kişi başına düşen yıllık ortalama CO2 emisyonu.',
                'birim': 'Ton',
                'metodoloji': 'Our World in Data (CO2 Data)'
            }
        }
