"""
workers.py — QThread tabanlı arka plan işçileri
DataWorker, ParquetLoadWorker, MapWorker, PdfExportWorker, IMFWorker
"""
import io, math, os, json
import pandas as pd
import numpy as np
import folium
import requests

from PyQt5.QtCore import QThread, pyqtSignal

from sbf_terminal.constants import INDICATORS, COUNTRY_TR, blacklist_path
from sbf_terminal.imf_api import IMFApiClient

try:
    import wbgapi as wb
except ImportError:
    wb = None


# ── Blacklist yardımcıları ─────────────────────────────────────────────────────────────
def _load_blacklist():
    """Kara listeyi diskten yükler. Döndürür: {wb_code: timestamp_str}"""
    if not os.path.exists(blacklist_path):
        return {}
    try:
        with open(blacklist_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_blacklist(blacklist: dict):
    """Kara listeyi diske kaydeder."""
    try:
        with open(blacklist_path, 'w', encoding='utf-8') as f:
            json.dump(blacklist, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Blacklist] Kaydedilemedi: {e}")


# ── DataWorker ─────────────────────────────────────────────────────────────────
class DataWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    INDICATORS = INDICATORS  # class-level referans

    def __init__(self, years=None, new_keys=None):
        super().__init__()
        self.years    = years    if years    else list(range(2023, 2026))
        self.new_keys = new_keys if new_keys else []

    def run(self):
        try:
            if wb is None:
                raise ImportError("wbgapi kütüphanesi eksik!")
            from datetime import datetime
            inds = self.INDICATORS
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

            # Kara listeyi yükle
            blacklist = _load_blacklist()
            if blacklist:
                print(f"[Blacklist] Kara listede {len(blacklist)} gösterge kodu var, atlanıyor.")

            self.progress.emit(10)
            chunk_size = 3
            new_keys_set = set(self.new_keys)

            # Kara listedeki kodları filtrele
            def is_blacklisted(k):
                if k in blacklist:
                    name = inds.get(k, k)
                    print(f"[Blacklist] ATLANDI: {name} ({k}) → {blacklist[k]}")
                    return True
                return False

            indicator_keys_new = [k for k in inds.keys() if k != 'HD.HCI.OVRL' and k in new_keys_set and not is_blacklisted(k)]
            indicator_keys_old = [k for k in inds.keys() if k != 'HD.HCI.OVRL' and k not in new_keys_set and not is_blacklisted(k)]

            work_groups = []
            if indicator_keys_new:
                work_groups.append((indicator_keys_new, range(2000, 2026), 'YENİ GÖSTERGE (25 yıl)'))
            if indicator_keys_old:
                work_groups.append((indicator_keys_old, self.years, f'MEVCUT ({len(self.years)} yıl)'))

            total_keys = len(indicator_keys_new) + len(indicator_keys_old)
            total_chunks = math.ceil(total_keys / chunk_size)
            fdf_main = None
            chunk_counter = 0

            for group_keys, group_years, group_label in work_groups:
                print(f"[DataWorker] → {group_label}: {len(group_keys)} gösterge")
                for i in range(0, len(group_keys), chunk_size):
                    chunk = group_keys[i:i + chunk_size]
                    self.progress.emit(10 + int(70 * chunk_counter / total_chunks))
                    chunk_counter += 1
                    try:
                        _pool = ThreadPoolExecutor(max_workers=1)
                        _future = _pool.submit(wb.data.DataFrame, chunk, time=group_years)
                        try:
                            cdf = _future.result(timeout=240)
                        except FuturesTimeout:
                            ts = datetime.now().strftime('%Y-%m-%d %H:%M')
                            for k in chunk:
                                blacklist[k] = ts
                                print(f"[Blacklist] EKLENDİ: {inds.get(k, k)} ({k}) → {ts}")
                            _save_blacklist(blacklist)
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
                    except Exception as ex:
                        print(f"Kısmi Çekim Hatası ({chunk}):", ex)
                    self.progress.emit(10 + int(70 * chunk_counter / total_chunks))

            try:
                self.progress.emit(85)
                _pool = ThreadPoolExecutor(max_workers=1)
                _future = _pool.submit(wb.data.DataFrame, 'HD.HCI.OVRL', time=range(2000, 2026), db=63)
                cdf_hdi = _future.result(timeout=240)
                _pool.shutdown(wait=False)
                cdf_hdi = cdf_hdi.stack().to_frame(name='v').reset_index()
                if len(cdf_hdi.columns) == 4:
                    cdf_hdi.columns = ['ISO', 'Series', 'Yıl', 'Val']
                    cdf_hdi = cdf_hdi.pivot_table(index=['ISO', 'Yıl'], columns='Series', values='Val', aggfunc='first')
                else:
                    cdf_hdi.columns = ['ISO', 'Yıl', 'Val']
                    cdf_hdi = cdf_hdi.set_index(['ISO', 'Yıl'])
                    cdf_hdi.columns = ['HD.HCI.OVRL']
                if fdf_main is None:
                    fdf_main = cdf_hdi
                else:
                    fdf_main = pd.merge(fdf_main, cdf_hdi, left_index=True, right_index=True, how='outer')
            except Exception as e:
                print("HDI Çekim Hatası:", e)

            if fdf_main is None:
                raise Exception("Hiçbir veri çekilemedi. İnternet bağlantınızı kontrol edin.")

            fdf_main.reset_index(inplace=True)
            fdf_main['Yıl'] = fdf_main['Yıl'].astype(str).str.replace('YR', '').replace('', '0').astype(int)
            fdf_main.rename(columns=inds, inplace=True)

            ec = wb.economy.DataFrame()[['name', 'longitude', 'latitude', 'incomeLevel', 'region', 'aggregate']]
            fdf = pd.merge(fdf_main, ec, left_on='ISO', right_index=True)
            fdf = fdf[fdf['aggregate'] == False]
            fdf.rename(columns={'name': 'Ülke', 'longitude': 'Lon', 'latitude': 'Lat', 'incomeLevel': 'Gelir_Grubu'}, inplace=True)
            fdf = fdf.sort_values(['ISO', 'Yıl'])

            for col in inds.values():
                if col in fdf.columns:
                    fdf[col] = pd.to_numeric(fdf[col], errors='coerce')

            if 'Top10' in fdf.columns and 'Low20' in fdf.columns and 'Sec20' in fdf.columns:
                low40 = pd.to_numeric(fdf['Low20'], errors='coerce') + pd.to_numeric(fdf['Sec20'], errors='coerce')
                fdf['palma_ratio'] = pd.to_numeric(fdf['Top10'], errors='coerce') / low40.replace(0, np.nan)
            if 'Top10' in fdf.columns and 'Bottom10' in fdf.columns:
                fdf['WIID_Ratio'] = np.where(fdf['Bottom10'] > 0, fdf['Top10'] / fdf['Bottom10'], np.nan)

            self.progress.emit(95)
            self.finished.emit(fdf)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.error.emit(str(e))


# ── ParquetLoadWorker ──────────────────────────────────────────────────────────
class ParquetLoadWorker(QThread):
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            df = pd.read_parquet(self.path, engine='pyarrow')
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))


# ── MapWorker ─────────────────────────────────────────────────────────────────
class MapWorker(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, df_y, year, theme, lang='tr'):
        super().__init__()
        self.df_y  = df_y
        self.year  = year
        self.theme = theme
        self.lang  = lang

    def run(self):
        try:
            m = folium.Map(
                location=[20, 0], zoom_start=2,
                tiles='CartoDB positron' if self.theme == 'light' else 'CartoDB dark_matter',
                control_scale=True
            )
            if self.df_y is not None and not self.df_y.empty:
                # GSYİH olan ülkeler: kırmızı normal nokta
                df_with_gdp = self.df_y.dropna(subset=['Lon', 'Lat', 'GSYİH'])
                # GSYİH olmayan ama Lon/Lat ve en az 1 göstergesi olan ülkeler: gri küçük nokta
                has_gdp_isos = set(df_with_gdp['ISO'].unique())
                df_no_gdp = self.df_y[
                    (~self.df_y['ISO'].isin(has_gdp_isos)) &
                    self.df_y['Lon'].notna() & self.df_y['Lat'].notna()
                ].drop_duplicates('ISO')

                for _, r in df_with_gdp.iterrows():
                    tooltip_name = COUNTRY_TR.get(r['Ülke'], r['Ülke']) if self.lang == 'tr' else r['Ülke']
                    folium.CircleMarker(
                        location=[r['Lat'], r['Lon']],
                        radius=7,
                        color='#8d6e63', weight=1.5,
                        fill=True, fill_color='#d64111', fill_opacity=0.7,
                        tooltip=f"<div style='font-size:18px; font-weight:bold; padding:4px;'>{tooltip_name}</div>",
                        className=f"iso_{r['ISO']}"
                    ).add_to(m)

                for _, r in df_no_gdp.iterrows():
                    tooltip_name = COUNTRY_TR.get(r['Ülke'], r['Ülke']) if self.lang == 'tr' else r['Ülke']
                    extra_info = ""
                    if 'Büyüme' in r and not pd.isna(r['Büyüme']):
                        growth_label = "Growth" if self.lang == 'en' else "Büyüme"
                        extra_info = f"<br><span style='font-size:12px;color:#aaa;'>{growth_label}: {r['Büyüme']:.1f}%</span>"
                    folium.CircleMarker(
                        location=[r['Lat'], r['Lon']],
                        radius=5,
                        color='#666', weight=1.5,
                        fill=True, fill_color='#999', fill_opacity=0.6,
                        tooltip=f"<div style='font-size:18px; font-weight:bold; padding:4px;'>{tooltip_name}{extra_info}</div>",
                        className=f"iso_{r['ISO']}"
                    ).add_to(m)


            script = """
            <script>
            (function() {
                var attempts = 0;
                var bindInterval = setInterval(function() {
                    var items = document.querySelectorAll('path.leaflet-interactive');
                    if (items.length > 0 || attempts > 20) {
                        clearInterval(bindInterval);
                        items.forEach(function(p) {
                            var cls = p.getAttribute('class') || "";
                            var classes = cls.split(' ');
                            for (var i = 0; i < classes.length; i++) {
                                var c = classes[i];
                                if (c.indexOf("iso_") === 0) {
                                    var isoCode = c.substring(4);
                                    p.style.cursor = "pointer";
                                    p.addEventListener("mousedown", function(e) {
                                        document.title = 'select://' + isoCode;
                                    }, true);
                                    break;
                                }
                            }
                        });
                    }
                    attempts++;
                }, 200);
            })();
            </script>
            """
            m.get_root().html.add_child(folium.Element(script))
            buf = io.BytesIO()
            m.save(buf, close_file=False)
            html = buf.getvalue().decode('utf-8')
            self.finished.emit(html)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.error.emit(str(e))


# ── PdfExportWorker ───────────────────────────────────────────────────────────
class PdfExportWorker(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, fig, fn, success_message):
        super().__init__()
        self.fig = fig
        self.fn  = fn
        self.success_message = success_message

    def run(self):
        try:
            self.fig.write_image(self.fn, format="pdf")
            self.finished.emit(self.success_message)
        except Exception as e:
            self.error.emit(str(e))


# ── IMFWorker ─────────────────────────────────────────────────────────────────
class IMFWorker(QThread):
    """IMF IFS SDMX API'den IPI ve PPI verilerini çeker (modüler istemci ile)."""
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    def run(self):
        try:
            result = IMFApiClient.fetch_all_default()
            self.finished.emit(result)
        except Exception as e:
            print(f"[IMF] Beklenmeyen hata: {e}")
            self.finished.emit(None)
