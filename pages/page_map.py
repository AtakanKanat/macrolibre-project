"""
page_map.py — Mixin: Genel Harita (Page 0)
Update map, country selection, info panel rendering.
"""
import os
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView

from sbf_terminal.workers import MapWorker
from sbf_terminal.constants import COUNTRY_TR, COUNTRY_TR_REV


class MapMixin:
    """Page 0 — Genel Harita ve Ülke Bilgi Paneli."""

    def update_map(self):
        try:
            if self.df is None:
                return
            try:
                y = int(self.combo.currentText())
            except Exception:
                return
            df_y = self.df[self.df['Yıl'] == y].copy()
            self._map_worker = MapWorker(df_y, y, self.current_theme, self.current_lang)
            self._map_worker.finished.connect(self._on_map_ready)
            self._map_worker.error.connect(lambda e: print(f'[Map] Hata: {e}'))
            self._map_worker.start()
        except Exception as e:
            print(f'[update_map] Hata: {e}')

    def _on_map_ready(self, html):
        try:
            self.wv.setHtml(html)
        except Exception as e:
            print(f'[_on_map_ready] Hata: {e}')

    def on_map_title_changed(self, title):
        try:
            if title.startswith('select://'):
                iso = title.replace('select://', '').split('/')[0]
                self.on_country_selected(iso)
                QTimer.singleShot(50, lambda: self.wv.page().runJavaScript('document.title="";'))
        except Exception as e:
            print(f'[on_map_title_changed] Hata: {e}')

    def on_country_selected(self, iso):
        try:
            if self.df is None:
                return
            rows = self.df[self.df['ISO'] == iso]
            if rows.empty:
                return
            self.current_country_iso = iso
            country_en = rows.iloc[0]['Ülke']
            display_name = self._display_country(country_en)
            if hasattr(self, 'search_combo'):
                self.search_combo.blockSignals(True)
                self.search_combo.setCurrentText(display_name)
                self.search_combo.blockSignals(False)
            self.ui_refresh()
        except Exception as e:
            print(f'[on_country_selected] Hata: {e}')

    def clear_info(self):
        self.li.clear()
        if hasattr(self, 'li_map'):
            self.li_map.setHtml("")

    def copy_to_clipboard(self):
        text = self.li.toPlainText()
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Kopyalandı", "Analiz verileri panoya kopyalandı.")
