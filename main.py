"""
main.py - SBF Terminal Başlangıç Noktası
"""
import sys
import os
import types

# Bu dosyanın bulunduğu dizin (0.8.0) sbf_terminal paketi olarak kayıt altına alınır.
# Böylece klasör adı ne olursa olsun 'from sbf_terminal...' import'ları çalışır.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)

# Üst dizini path'e ekle (sbf_terminal araması için)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Eğer sbf_terminal henüz import edilmemişse, 0.8.0 klasörünü sbf_terminal olarak kayıt et
if 'sbf_terminal' not in sys.modules:
    _pkg = types.ModuleType('sbf_terminal')
    _pkg.__path__ = [_this_dir]
    _pkg.__package__ = 'sbf_terminal'
    _pkg.__spec__ = None
    sys.modules['sbf_terminal'] = _pkg

from PyQt5.QtWidgets import QApplication
from sbf_terminal.main_window import TicaretTerminalWindow
from sbf_terminal.utils import log_crash

def main():
    app = QApplication(sys.argv)
    try:
        ex = TicaretTerminalWindow()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        log_crash(e)

if __name__ == '__main__':
    main()
