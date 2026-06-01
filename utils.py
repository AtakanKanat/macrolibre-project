"""
utils.py — Yardımcı fonksiyonlar
Plotly helper, ekonomi formatlayıcı, crash logger.
"""
import os, time, ctypes, tempfile


# ── Akıllı Ekonomi Birim Formatı ──────────────────────────────────────────────
def get_econ_fmt(lang='tr'):
    def _fmt(x, pos=None):
        """Trilyon = T $, Milyar = mr $ (TR) / B $ (EN), endeksler 3 ondalık."""
        try:
            x = float(x)
        except Exception:
            return str(x)
        if abs(x) >= 1e12:
            return f"{x / 1e12:.2f} T $"
        elif abs(x) >= 1e9:
            bil_str = "mr $" if lang == 'tr' else "B $"
            return f"{x / 1e9:.2f} {bil_str}"
        elif abs(x) <= 2.0 and abs(x) > 0:
            return f"{x:,.3f}"
        else:
            return f"{x:,.1f}"
    return _fmt


# ── Crash Logger ───────────────────────────────────────────────────────────────
def log_crash(e):
    try:
        with open("crash_report.txt", "w", encoding="utf-8") as f:
            f.write(f"Crash Log: {time.ctime()}\n{str(e)}")
    except Exception:
        pass
    try:
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Uygulama başlatılamadı.\nHata: {str(e)}\n\nLütfen 'crash_report.txt' dosyasını kontrol edin.",
            "Mülkiye Terminal - Kritik Hata",
            0x10
        )
    except Exception:
        pass


# ── Plotly Geçici Dizin Başlatıcı ─────────────────────────────────────────────
def _init_plotly_tmp():
    """Uygulama başlangıcında plotly.min.js'i bir kez geçici klasöre kopyala."""
    import plotly as _p, shutil
    d = tempfile.mkdtemp(prefix='sbf_plotly_')
    shutil.copy2(
        os.path.join(os.path.dirname(_p.__file__), 'package_data', 'plotly.min.js'),
        os.path.join(d, 'plotly.min.js')
    )
    return d


# Modül yüklendiğinde bir kez çalıştır
_PLOTLY_TMP_DIR = _init_plotly_tmp()


# ── Plotly Figürünü QWebEngineView'e Yükle ────────────────────────────────────
def _load_plotly_to_view(web_view, fig):
    """Plotly figürünü QWebEngineView'e yükler (same-origin policy uyumlu)."""
    from PyQt5.QtCore import QUrl
    fig_json = fig.to_json()
    html = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script>
/* PyQt5 Chromium :focus-visible yaması — plotly.min.js yüklenmeden önce */
(function(){
  var orig = CSSStyleSheet.prototype.insertRule;
  CSSStyleSheet.prototype.insertRule = function(rule, idx) {
    try { return orig.call(this, rule, idx); } catch(e) {}
  };
})();
</script>
<script src="plotly.min.js"></script>
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:#fafafa; overflow-x:hidden;}
  #c{width:100vw; min-height:100vh;}
</style>
</head><body><div id="c"></div><script>
var f=FIGJSON;
var layout=Object.assign({},f.layout);
if(layout.height && layout.height > 100) {
  document.getElementById('c').style.height = layout.height + 'px';
} else {
  layout.height = null;
}
layout.autosize = true;
layout.width = null;

var xAll=[];
(f.data||[]).forEach(function(t){if(t.x&&t.x.length)xAll=xAll.concat(t.x);});
if(xAll.length&&typeof xAll[0]==='number' && (!layout.xaxis || typeof layout.xaxis.range === 'undefined')){
  var mn=Math.min.apply(null,xAll),mx=Math.max.apply(null,xAll);
  var pad=(mx-mn)*0.02;
  layout.xaxis=Object.assign({},layout.xaxis||{},{range:[mn-pad,mx+pad]});
}
Plotly.react('c',f.data,layout,{responsive:true,displayModeBar:false});
window.addEventListener('load',function(){Plotly.Plots.resize('c');});
setTimeout(function(){Plotly.Plots.resize('c');},200);
</script></body></html>""".replace("FIGJSON", fig_json)

    html_path = os.path.join(_PLOTLY_TMP_DIR, f'chart_{id(web_view)}_{int(time.time()*1000)}.html')
    with open(html_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    web_view.load(QUrl.fromLocalFile(html_path))
