"""
imf_api.py - IMF API client
Handles fetching and parsing of macroeconomic indicators from the IMF SDMX API.
"""
import requests
import pandas as pd
import xml.etree.ElementTree as ET

class IMFApiClient:
    BASE_URL = "https://dataservices.imf.org/REST/sdmx/2.1/CompactData/IFS"
    
    DEFAULT_INDICATORS = {
        'AIP_IX':  'IPI',
        'PPPI_IX': 'PPI',
    }
    
    @classmethod
    def fetch_indicator(cls, code, col_name, start_year=2000, end_year=2025):
        """
        Fetches a specific indicator from the IMF API.
        Returns a pandas DataFrame or None if failed.
        """
        url = f"{cls.BASE_URL}/A..{code}?startPeriod={start_year}&endPeriod={end_year}"
        try:
            resp = requests.get(url, timeout=90, headers={'Accept': 'application/xml'})
            if resp.status_code != 200:
                print(f"[IMF API] {code}: HTTP {resp.status_code}")
                return None
            
            root = ET.fromstring(resp.content)
            rows = []
            for elem in root.iter():
                tag = elem.tag.split('}')[-1]
                if tag == 'Series':
                    iso = elem.attrib.get('REF_AREA', '')
                    if not iso:
                        continue
                    for obs in elem:
                        otag = obs.tag.split('}')[-1]
                        if otag == 'Obs':
                            yr  = obs.attrib.get('TIME_PERIOD', '')
                            val = obs.attrib.get('OBS_VALUE', '')
                            try:
                                rows.append({'ISO': iso, 'Yıl': int(yr), col_name: float(val)})
                            except (ValueError, TypeError):
                                pass
            if rows:
                print(f"[IMF API] {code} ({col_name}): {len(rows)} gözlem")
                return pd.DataFrame(rows)
            else:
                print(f"[IMF API] {code}: gözlem bulunamadı")
                return None
        except requests.exceptions.ConnectionError:
            print(f"[IMF API] Sunucuya ulaşılamıyor. {code} atlandı.")
            return None
        except Exception as ex:
            print(f"[IMF API] {code} hatası: {ex}")
            return None
            
    @classmethod
    def fetch_all_default(cls, start_year=2000, end_year=2025):
        """
        Fetches all default indicators and merges them into a single DataFrame.
        """
        frames = []
        for code, col in cls.DEFAULT_INDICATORS.items():
            df = cls.fetch_indicator(code, col, start_year, end_year)
            if df is not None and not df.empty:
                frames.append(df)
        
        if not frames:
            return None
            
        result = frames[0]
        for f in frames[1:]:
            result = pd.merge(result, f, on=['ISO', 'Yıl'], how='outer')
        return result
