import pandas as pd
import wbgapi as wb
from .base_plugin import BasePlugin

class OWIDPovertyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "OWID Poverty Data"

    def fetch_data(self) -> pd.DataFrame:
        url = "https://raw.githubusercontent.com/owid/poverty-data/master/datasets/pip_dataset.csv"
        print(f"[{self.name}] İndiriliyor: {url}")
        df = pd.read_csv(url)
        
        # PIP dataset'te ISO kodu yok, wbgapi üzerinden isimle eşleştirelim
        try:
            ec = wb.economy.DataFrame()[['name']].reset_index()
            # name -> id (ISO)
            name_to_iso = dict(zip(ec['name'], ec['id']))
            # Özel OWID eşleşmeleri (bazen farklı yazılır)
            name_to_iso.update({
                'United States': 'USA',
                'United Kingdom': 'GBR',
                'South Korea': 'KOR',
                'Russia': 'RUS',
                'Democratic Republic of Congo': 'COD',
                'Congo': 'COG',
                'Egypt': 'EGY',
                'Iran': 'IRN',
                'Turkey': 'TUR',
                'Venezuela': 'VEN',
                'Yemen': 'YEM'
            })
            df['ISO'] = df['country'].map(name_to_iso)
            df = df[df['ISO'].notna()]
        except Exception as e:
            print(f"[{self.name}] ISO haritalama hatası: {e}")
            return pd.DataFrame()

        cols_to_keep = {
            'ISO': 'ISO',
            'year': 'Yıl',
            'headcount_ratio_215': 'Mutlak Yoksulluk (%)', # PIP dataset uses headcount_ratio_international_povline for $2.15
            'headcount_ratio_international_povline': 'Mutlak Yoksulluk (%)',
            'gini': 'OWID Gini'
        }
        
        existing_cols = [c for c in cols_to_keep.keys() if c in df.columns]
        df = df[existing_cols].rename(columns=cols_to_keep)
        
        df = df[df['Yıl'] >= 1990].copy()
        
        # Eğer welfare_type veya diğer kırılımlardan dolayı aynı ülke/yıl için birden fazla satır varsa ilkini al
        if not df.empty:
            df = df.groupby(['ISO', 'Yıl']).first().reset_index()
            
        return df

    def get_metadata(self) -> dict:
        return {
            'Mutlak Yoksulluk (%)': {
                'tanim': 'Uluslararası yoksulluk sınırının (günlük $2.15) altında yaşayan nüfusun yüzdesi.',
                'birim': '%',
                'metodoloji': 'Our World in Data (PIP Dataset)'
            },
            'OWID Gini': {
                'tanim': 'Gelir eşitsizliğini ölçen Gini katsayısı (0 tam eşitlik, 100 tam eşitsizlik).',
                'birim': '0-100',
                'metodoloji': 'Our World in Data (PIP Dataset)'
            }
        }
