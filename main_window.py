"""
main_window.py — Ana Pencere (TicaretTerminalWindow)
Tüm mixinleri miras alır ve UI başlatmasını, çeviri / tema yönetimini sağlar.
"""
import sys, os, time
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QProgressBar, QStackedWidget, QComboBox, QTextEdit, QApplication, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCompleter, QStylePainter, QStyleOptionComboBox, QStyle, QMenu, QAction,
    QLineEdit, QFileDialog, QGridLayout, QCheckBox, QDoubleSpinBox, QListView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import plotly.graph_objects as go

from sbf_terminal.constants import COUNTRY_TR, COUNTRY_TR_REV, parquet_path, social_csv_path
from sbf_terminal.utils import _load_plotly_to_view, get_econ_fmt, log_crash
from sbf_terminal.widgets import CheckableComboBox, CustomWebPage
from sbf_terminal.workers import ParquetLoadWorker, DataWorker, MapWorker, IMFWorker
from sbf_terminal.data_engine import SmartDataEngine, merge_social_indicators
from sbf_terminal.i18n import get_text, LANGS

# Mixins
from sbf_terminal.pages.page_map import MapMixin
from sbf_terminal.pages.page_macro import MacroMixin
from sbf_terminal.pages.page_devdist import DevDistMixin
from sbf_terminal.pages.page_rankings import RankingsMixin
from sbf_terminal.pages.page_public import PublicMixin
from sbf_terminal.pages.page_sectoral import SectoralMixin
from sbf_terminal.pages.page_risk import RiskMixin
from sbf_terminal.pages.page_correlation import CorrelationMixin
from sbf_terminal.pages.page_energy import EnergyMixin

class TicaretTerminalWindow(
    QMainWindow,
    MapMixin,
    MacroMixin,
    DevDistMixin,
    RankingsMixin,
    PublicMixin,
    SectoralMixin,
    RiskMixin,
    CorrelationMixin,
    EnergyMixin
):
    """Ana Terminal Sınıfı - Tüm Mixin'leri Miras Alır"""
    
    def t(self, key):
        """Çok dilli metinleri döndürür"""
        return get_text(getattr(self, 'current_lang', 'tr'), key)

    def __init__(self):
            super().__init__()
            self.df = None
            self.macro_mode = "period"  # "period" or "instant"
            self.corr_mode = "instant"  # "period" or "instant"
            self.p1_cache = {}

            try:
                self.themes = {
                    'light': {'bg': '#f0f2f5', 'sidebar': '#2c3e50', 'text': '#2c3e50', 'card': '#ffffff', 'border': '#d5d8dc', 'header': '#ecf0f1', 'btn_nav': '#34495e', 'chart_bg': '#ffffff'},
                    'dark': {'bg': '#121212', 'sidebar': '#1e1e1e', 'text': '#e0e0e0', 'card': '#1e1e1e', 'border': '#333333', 'header': '#2d2d2d', 'btn_nav': '#2c3e50', 'chart_bg': '#1e1e1e'}
                }
                self.current_theme = 'light'
                self.setWindowTitle("SBF Makro Veri Analiz Merkezi")
                self.setMinimumSize(1000, 750)
                self.resize(1600, 950)
            
                cw = QWidget(); self.setCentralWidget(cw)
                main_layout = QHBoxLayout(cw); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
            
                # SIDEBAR
                self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar")
                self.sidebar.setMinimumWidth(210)
                sl = QVBoxLayout(self.sidebar); sl.setContentsMargins(10, 20, 10, 20); sl.setSpacing(10)
            
                self.logo = QLabel("🏛️ SBF\nMAKRO TERMİNAL"); self.logo.setAlignment(Qt.AlignCenter)
                self.logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #ecf0f1; border-bottom: 2px solid #34495e; padding-bottom: 10px;")
                sl.addWidget(self.logo); sl.addSpacing(20)
            
                self.update_btn = QPushButton("🌐 Verileri Güncelle")
                self.update_btn.clicked.connect(self.start_data_update)
                sl.addWidget(self.update_btn)

                self.clear_blacklist_btn = QPushButton("🗑️ Kara Listeyi Temizle")
                self.clear_blacklist_btn.setToolTip("Zaman aşımına uğrayan göstergelerin kara listesini temizler\nBir sonraki güncellemede tekrar denenecekler.")
                self.clear_blacklist_btn.clicked.connect(self.clear_timeout_blacklist)
                sl.addWidget(self.clear_blacklist_btn)
            
                self.progress_bar = QProgressBar()
                self.progress_bar.setVisible(False)
                self.progress_bar.setFixedHeight(12)
                sl.addWidget(self.progress_bar)
            
                def create_nav_btn(text, idx):
                    b = QPushButton(text); b.target_idx = idx; b.clicked.connect(lambda _, x=idx: self.switch_page(x)); return b
                self.btn_nav_map   = create_nav_btn("🏠 Genel Harita", 0)
                self.btn_nav_macro  = create_nav_btn("📊 Makroekonomi", 1)
                self.btn_nav_pub    = create_nav_btn("🏛️ Kamu Maliyesi", 4)
                self.btn_nav_rd     = create_nav_btn("🌱 Kalkınma & Bölüşüm", 2)
                self.btn_nav_block  = create_nav_btn("📊 Küresel Sıralamalar", 3)
                self.btn_nav_sector = create_nav_btn("🏗️ Sektörel Paylar", 5)
                self.btn_nav_risk   = create_nav_btn("⚠️ Risk Analizi", 6)
                self.btn_nav_corr   = create_nav_btn("🔗 Korelasyon", 7)
                self.btn_nav_energy = create_nav_btn("⚡ Enerji Ekonomisi", 8)
                # nav_btns listesindeki SİRA sidebar görünümü ile eşleşmeli
                self.nav_btns = [
                    self.btn_nav_map,    # pos 0 → page 0
                    self.btn_nav_macro,  # pos 1 → page 1
                    self.btn_nav_rd,     # pos 2 → page 3
                    self.btn_nav_block,  # pos 3 → page 4
                    self.btn_nav_pub,    # pos 4 → page 6
                    self.btn_nav_sector, # pos 5 → page 7
                    self.btn_nav_risk,   # pos 6 → page 8
                    self.btn_nav_corr,   # pos 7 → page 9
                    self.btn_nav_energy, # pos 8 → page 10
                ]
                for b in self.nav_btns: sl.addWidget(b)
            
                sl.addStretch()
                self.btn_theme_toggle = QPushButton("🌙 Karanlık Mod"); self.btn_theme_toggle.clicked.connect(self.toggle_theme)
                sl.addWidget(self.btn_theme_toggle)
            
                self.btn_lang_toggle = QPushButton("🌐 English"); self.btn_lang_toggle.clicked.connect(self.switch_language)
                sl.addWidget(self.btn_lang_toggle)
            
                # MERKEZ
                self.stacked_widget = QStackedWidget()
            
                # PAGE 0
                page0 = QWidget(); p0l = QHBoxLayout(page0); p0l.setContentsMargins(10, 10, 10, 10)
                LP = QFrame(); LP.setObjectName("analysis_panel")
                LP.setMinimumWidth(380)
                LL = QVBoxLayout(LP)
                self.search_combo = QComboBox(); self.search_combo.setEditable(True); self.search_combo.setPlaceholderText("🔍 Ülke Seçin veya Arayın..."); 
                self.search_combo.setStyleSheet("padding:8px; font-size:14px; background:#fff; color:#8d6e63; border:1px solid #d5d8dc;"); 
                def search_trigger():
                    txt = self.search_combo.currentText()
                    if self.df is not None:
                        en_name = self._en_country(txt)
                        m = self.df[self.df['Ülke']==en_name]
                        if not m.empty: self.on_country_selected(m.iloc[0]['ISO'])
                self.search_combo.activated[str].connect(
                    lambda x: self.on_country_selected(
                        self.df[self.df['Ülke']==self._en_country(x)]['ISO'].iloc[0]
                    ) if self.df is not None and not self.df[self.df['Ülke']==self._en_country(x)].empty else None
                )
                self.search_combo.lineEdit().returnPressed.connect(search_trigger)
                LL.addWidget(self.search_combo)
            
                cmbL = QHBoxLayout(); self.lbl_statik = QLabel("Statik Analiz Yılı:"); self.lbl_statik.setStyleSheet("font-weight:bold; font-size:14px; border:none;")
                self.combo = QComboBox(); self.combo.addItems([str(y) for y in range(2000, 2026)]); self.combo.setCurrentText("2024")
                self.combo.currentTextChanged.connect(self.update_map)
                self.combo.currentTextChanged.connect(self.ui_refresh)
                cmbL.addWidget(self.lbl_statik); cmbL.addWidget(self.combo); LL.addLayout(cmbL)
            
                bl = QHBoxLayout()
                self.bu = QPushButton("Anlık Yenile"); self.bu.setStyleSheet("background:#1a5276; color:#fff; padding:10px; font-weight:bold;"); self.bu.clicked.connect(self.start_data_update)
                self.bc = QPushButton("Ekranı Temizle"); self.bc.setStyleSheet("background:#e67e22; color:#fff; padding:10px; font-weight:bold;"); self.bc.clicked.connect(self.clear_info)
                bl.addWidget(self.bu); bl.addWidget(self.bc); LL.addLayout(bl)
            
                # --- ANALYSIS TEXT ---
                self.li = QTextEdit(); self.li.setReadOnly(True); self.li.setStyleSheet("padding:8px; border-radius:5px; margin-top:10px;"); LL.addWidget(self.li)
                self.btn_copy = QPushButton("📋 Tüm Verileri Kopyala"); self.btn_copy.setStyleSheet("background-color:#27ae60; color:#fff; padding:10px; font-weight:bold;"); self.btn_copy.clicked.connect(self.copy_to_clipboard); LL.addWidget(self.btn_copy)
            
                self.wv = QWebEngineView(); self.wp = CustomWebPage(self); self.wv.setPage(self.wp)
                self.wv.titleChanged.connect(self.on_map_title_changed)
                p0l.addWidget(LP); p0l.addWidget(self.wv, 1)
                self.stacked_widget.addWidget(page0)
            
                # PAGE 1 (Makroekonomi)
                page1 = QWidget(); p1l = QVBoxLayout(page1)
            
                top_h = QHBoxLayout()
                self.lbl_macro_c = QLabel("Ülke/Bölge:")
                self.macro_c = CheckableComboBox() 
                self.macro_cmb = CheckableComboBox()
                self.macro_cmb.setMinimumWidth(180)
                self.macro_cmb.addItems(["GSYİH", "GSMH", "Enflasyon", "Büyüme", "İşsizlik", "Kişi Başı GSYİH", "Kişi Başı GSMH", "Kişi Başı GSYİH (SAGP)", "Kişi Başı GSMH (SAGP)", "Cari Denge", "Borç Oranı"])
                self.lbl_macro_ind = QLabel("Gösterge:")
                self.lbl_macro_per = QLabel("Dönem:")
                self.macro_start = QComboBox()
                self.macro_end = QComboBox()
                self.macro_price = QComboBox()
                self.macro_price.addItems(["Nominal", "Reel"])
                self.macro_price.setCurrentText("Reel")
                self.lbl_macro_price = QLabel("Fiyat:")
            
                self.btn_macro_mode = QPushButton("📍 Anlık")
                self.btn_macro_mode.setCheckable(True)
                self.btn_macro_mode.setFixedWidth(85)
                self.btn_macro_mode.clicked.connect(self.toggle_macro_mode)
            
                top_h.addWidget(self.lbl_macro_c); top_h.addWidget(self.macro_c)
                self.btn_clear_macro_c = QPushButton("🧹"); self.btn_clear_macro_c.setFixedWidth(30); self.btn_clear_macro_c.clicked.connect(self.macro_c.clearSelection); top_h.addWidget(self.btn_clear_macro_c)
                top_h.addWidget(self.lbl_macro_ind); top_h.addWidget(self.macro_cmb)
                self.btn_clear_macro_ind = QPushButton("🧹"); self.btn_clear_macro_ind.setFixedWidth(30); self.btn_clear_macro_ind.clicked.connect(self.macro_cmb.clearSelection); top_h.addWidget(self.btn_clear_macro_ind)
                top_h.addWidget(self.btn_macro_mode)
                top_h.addWidget(self.lbl_macro_per); top_h.addWidget(self.macro_start)
                self.lbl_macro_dash = QLabel("-")
                top_h.addWidget(self.lbl_macro_dash); top_h.addWidget(self.macro_end)
                top_h.addWidget(self.lbl_macro_price); top_h.addWidget(self.macro_price)
                top_h.addStretch()
                self.btn_export_macro = QPushButton("📑 Rapor Al"); self.btn_export_macro.clicked.connect(self.export_macro_pdf)
                top_h.addWidget(self.btn_export_macro)
                p1l.addLayout(top_h)
            
                for c in [self.macro_c, self.macro_start, self.macro_end, self.macro_cmb, self.macro_price]: 
                    c.currentTextChanged.connect(self.plot_macro)
                self.macro_cmb.currentTextChanged.connect(self.update_macro_ui)
            
                content_h = QHBoxLayout()
                self.macro_web = QWebEngineView()
                _sm = self.macro_web.settings()
                _sm.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _sm.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _sm.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.macro_web.setHtml("<body style='background:#fafafa;'></body>")
                content_h.addWidget(self.macro_web)
                p1l.addLayout(content_h)
            
                self.p1_narrative = QTextEdit(); self.p1_narrative.setReadOnly(True); self.p1_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#fef9e7; border-left:5px solid #f1c40f;")
                self.p1_narrative.setFixedHeight(160); p1l.addWidget(self.p1_narrative)
                self.stacked_widget.addWidget(page1)
            
                # PAGE 3 — Kalkınma & Bölüşüm
                page3 = QWidget(); p3l = QVBoxLayout(page3)

                # ── Kontrol Çubuğu ───────────────────────────────────────────
                top_h = QHBoxLayout()
                self.rd_country1 = CheckableComboBox(); self.rd_country2 = QComboBox()
                self.rd_start = QComboBox(); self.rd_start.addItems([str(y) for y in range(2000, 2026)]); self.rd_start.setCurrentText("2000")
                self.rd_end   = QComboBox(); self.rd_end.addItems([str(y) for y in range(2000, 2026)]);   self.rd_end.setCurrentText("2024")
                for c in [self.rd_country1, self.rd_country2, self.rd_start, self.rd_end]:
                    c.currentTextChanged.connect(self.update_risk)
                self.lbl_rd_c1  = QLabel("Ülkeler:"); top_h.addWidget(self.lbl_rd_c1);  top_h.addWidget(self.rd_country1)
                self.btn_clear_rd_c1 = QPushButton("🧹"); self.btn_clear_rd_c1.setFixedWidth(30); self.btn_clear_rd_c1.clicked.connect(self.rd_country1.clearSelection); top_h.addWidget(self.btn_clear_rd_c1)
                self.lbl_rd_c2  = QLabel("Ülke 2:"); self.lbl_rd_c2.setVisible(False); self.rd_country2.setVisible(False)
                self.lbl_rd_per = QLabel("Dönem:");  top_h.addWidget(self.lbl_rd_per)
                top_h.addWidget(self.rd_start); top_h.addWidget(QLabel("–")); top_h.addWidget(self.rd_end)
                top_h.addStretch()
                self.btn_export_risk = QPushButton("📑 Rapor Al"); self.btn_export_risk.clicked.connect(self.export_risk_pdf)
                top_h.addWidget(self.btn_export_risk)
                p3l.addLayout(top_h)

                # ── İki Grafik Paneli Yan Yana ────────────────────────────────
                charts_v = QVBoxLayout(); charts_v.setSpacing(8)

                # Sol (Üst): Kalkınma & Bölüşüm
                welfare_frame = QFrame(); welfare_frame.setObjectName("analysis_panel")
                welfare_vl = QVBoxLayout(welfare_frame); welfare_vl.setContentsMargins(6, 4, 6, 4); welfare_vl.setSpacing(4)
                welfare_top_h = QHBoxLayout()
                self.lbl_welfare = QLabel("🌱 Kalkınma ve Bölüşüm")
                self.lbl_welfare.setStyleSheet("font-weight:bold; font-size:11px; color:#1a5276; padding:2px;")
                welfare_top_h.addWidget(self.lbl_welfare); welfare_top_h.addStretch()
                self.btn_welf_opt = QPushButton("⚙️ Göstergeler")
                self.btn_welf_opt.setStyleSheet("padding: 2px 6px; font-weight:bold; background-color: #ecf0f1; border-radius:3px;")
                self.welf_menu = QMenu(self)
                self.act_hdi = QAction("HDI", self, checkable=True); self.act_hdi.setChecked(True)
                self.act_ihdi = QAction("IHDI", self, checkable=True)
                self.act_phdi = QAction("PHDI", self, checkable=True)
                self.act_gdi = QAction("GDI", self, checkable=True)
                self.act_pisa = QAction("PISA", self, checkable=True)
                for act in [self.act_hdi, self.act_ihdi, self.act_phdi, self.act_gdi, self.act_pisa]:
                    act.triggered.connect(self.draw_welfare_chart); self.welf_menu.addAction(act)
                self.btn_welf_opt.setMenu(self.welf_menu); welfare_top_h.addWidget(self.btn_welf_opt)
                welfare_vl.addLayout(welfare_top_h)
            
                self.rd_welfare_web = QWebEngineView()
                _sw = self.rd_welfare_web.settings()
                _sw.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _sw.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _sw.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.rd_welfare_web.setHtml("<body style='background:#fafafa;'></body>")
                welfare_vl.addWidget(self.rd_welfare_web)
                charts_v.addWidget(welfare_frame, 55)

                # Sağ (Alt): Eşitsizlik
                ineq_frame = QFrame(); ineq_frame.setObjectName("analysis_panel")
                ineq_vl = QVBoxLayout(ineq_frame); ineq_vl.setContentsMargins(6, 4, 6, 4); ineq_vl.setSpacing(4)
                ineq_top_h = QHBoxLayout()
                self.lbl_ineq = QLabel("⚖️ Eşitsizlik Karşılaştırması")
                self.lbl_ineq.setStyleSheet("font-weight:bold; font-size:11px; color:#922b21; padding:2px;")
                ineq_top_h.addWidget(self.lbl_ineq); ineq_top_h.addStretch()
                self.btn_ineq_opt = QPushButton("⚙️ Göstergeler")
                self.btn_ineq_opt.setStyleSheet("padding: 2px 6px; font-weight:bold; background-color: #ecf0f1; border-radius:3px;")
                self.ineq_menu = QMenu(self)
                self.act_gini = QAction("Gini (WB)", self, checkable=True); self.act_gini.setChecked(True)
                self.act_owid_gini = QAction("Gini (OWID)", self, checkable=True); self.act_owid_gini.setChecked(True)
                self.act_palma = QAction("Palma", self, checkable=True)
                self.act_wiid = QAction("WIID", self, checkable=True)
                self.act_gii = QAction("GII", self, checkable=True)
                self.act_pov = QAction("Mutlak Yoksulluk ($2.15)", self, checkable=True); self.act_pov.setChecked(True)
                for act in [self.act_gini, self.act_owid_gini, self.act_palma, self.act_wiid, self.act_gii, self.act_pov]:
                    act.triggered.connect(self.draw_inequality_chart); self.ineq_menu.addAction(act)
                self.btn_ineq_opt.setMenu(self.ineq_menu); ineq_top_h.addWidget(self.btn_ineq_opt)
                ineq_vl.addLayout(ineq_top_h)
            
                self.rd_ineq_web = QWebEngineView()
                _si = self.rd_ineq_web.settings()
                _si.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _si.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _si.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.rd_ineq_web.setHtml("<body style='background:#fafafa;'></body>")
                ineq_vl.addWidget(self.rd_ineq_web)
                charts_v.addWidget(ineq_frame, 45)

                p3l.addLayout(charts_v, 90)

                # ── Narrative ─────────────────────────────────────────────────
                self.p3_narrative = QTextEdit(); self.p3_narrative.setReadOnly(True)
                self.p3_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#fef9e7; border-left:5px solid #f1c40f;")
                self.p3_narrative.setFixedHeight(110); p3l.addWidget(self.p3_narrative)
                self.stacked_widget.addWidget(page3)
            
                # PAGE 4 (Küresel Sıralamalar)
                page4 = QWidget(); p4l = QVBoxLayout(page4)
                top_h_blk = QHBoxLayout()
                self.lbl_blk_ind = QLabel("Gösterge Seçiniz:")
                self.blk_cmb = QComboBox()
                self.lbl_blk_year = QLabel("Yıl:")
                self.blk_year = QComboBox()
                self.blk_year.addItems([str(y) for y in range(2000, 2026)])
                self.blk_year.setCurrentText("2024")
                self.lbl_blk_price = QLabel("Fiyat Türü:")
                self.blk_price = QComboBox()
                self.blk_price.addItems(["Reel", "Nominal"])
                self.blk_price.setCurrentText("Reel")
                top_h_blk.addWidget(self.lbl_blk_ind); top_h_blk.addWidget(self.blk_cmb)
                top_h_blk.addWidget(self.lbl_blk_year); top_h_blk.addWidget(self.blk_year)
                top_h_blk.addWidget(self.lbl_blk_price); top_h_blk.addWidget(self.blk_price)
                top_h_blk.addStretch()
                self.blk_cmb.currentTextChanged.connect(self.plot_blocks)
                self.blk_year.currentTextChanged.connect(self.plot_blocks)
                self.blk_price.currentTextChanged.connect(self.plot_blocks)
                p4l.addLayout(top_h_blk)
            
                content_h_blk = QHBoxLayout()
                self.blk_web = QWebEngineView()
                _sb = self.blk_web.settings()
                _sb.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _sb.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _sb.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.blk_web.setHtml("<body style='background:#fafafa;'></body>")
                content_h_blk.addWidget(self.blk_web)
                p4l.addLayout(content_h_blk)
                self.p4_narrative = QTextEdit(); self.p4_narrative.setReadOnly(True); self.p4_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#fef9e7; border-left:5px solid #f1c40f;")
                self.p4_narrative.setFixedHeight(75); p4l.addWidget(self.p4_narrative)
                self.stacked_widget.addWidget(page4)
            
                # PAGE 6 (Kamu Maliyesi)
                page6 = QWidget(); p6l = QVBoxLayout(page6)
                pub_top_h = QHBoxLayout()
            
                self.lbl_pub_c = QLabel("Ülke/Bölge:")
                self.pub_c = CheckableComboBox()
            
                self.lbl_pub_ind = QLabel("Gösterge:")
                self.pub_ind = CheckableComboBox()
                self.pub_ind.setMinimumWidth(180)
                self.pub_ind.addItems(["Kamu Harcamaları", "Eğitim Harcamaları", "Sağlık Harcamaları", "Savunma Harcamaları", "Vergi Gelirleri", "Bütçe Dengesi", "Dış Borç", "Cari Denge"])
                for i in range(3):
                    it = self.pub_ind.model().item(i)
                    if it: it.setCheckState(Qt.Checked)
            
                self.lbl_pub_per = QLabel("Dönem:")
                self.pub_start = QComboBox()
                self.pub_end = QComboBox()
                self.btn_pub_mode = QPushButton("📍 Anlık")
                self.btn_pub_mode.setCheckable(True)
                self.btn_pub_mode.setFixedWidth(85)
                self.btn_pub_mode.clicked.connect(self.toggle_pub_mode)
            
                pub_top_h.addWidget(self.lbl_pub_c); pub_top_h.addWidget(self.pub_c)
                self.btn_clear_pub_c = QPushButton("🧹"); self.btn_clear_pub_c.setFixedWidth(30); self.btn_clear_pub_c.clicked.connect(self.pub_c.clearSelection); pub_top_h.addWidget(self.btn_clear_pub_c)
                pub_top_h.addWidget(self.lbl_pub_ind); pub_top_h.addWidget(self.pub_ind)
                self.btn_clear_pub_ind = QPushButton("🧹"); self.btn_clear_pub_ind.setFixedWidth(30); self.btn_clear_pub_ind.clicked.connect(self.pub_ind.clearSelection); pub_top_h.addWidget(self.btn_clear_pub_ind)
                pub_top_h.addWidget(self.btn_pub_mode)
                pub_top_h.addWidget(self.lbl_pub_per); pub_top_h.addWidget(self.pub_start)
                self.lbl_pub_dash = QLabel("-")
                pub_top_h.addWidget(self.lbl_pub_dash); pub_top_h.addWidget(self.pub_end)
                pub_top_h.addStretch()
                self.btn_export_pub = QPushButton("📑 Rapor Al"); self.btn_export_pub.clicked.connect(self.export_pub_pdf)
                pub_top_h.addWidget(self.btn_export_pub)
                p6l.addLayout(pub_top_h)
            
                self.pub_web = QWebEngineView()
                _spub = self.pub_web.settings()
                _spub.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _spub.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _spub.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.pub_web.setHtml("<body style='background:#fafafa;'></body>")
                p6l.addWidget(self.pub_web)
            
                self.pub_narrative = QTextEdit(); self.pub_narrative.setReadOnly(True)
                self.pub_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#eaf4fc; border-left:5px solid #2980b9; font-family:'Segoe UI',sans-serif; font-size:12px;")
                self.pub_narrative.setFixedHeight(160)
                p6l.addWidget(self.pub_narrative)
                self.stacked_widget.addWidget(page6)
                # PAGE 7 (Sektörel Paylar)
                page7 = QWidget(); p7l = QVBoxLayout(page7)
                sec_top_h = QHBoxLayout()
            
                self.lbl_sec_c = QLabel("Ülke/Bölge:")
                self.sec_c = CheckableComboBox()
            
                self.lbl_sec_ind = QLabel("Gösterge:")
                self.sec_ind = CheckableComboBox()
                self.sec_ind.addItems(["Tarım Payı", "Sanayi Payı", "Hizmetler Payı", "İmalat Payı", 
                                       "Enerji-Maden", "Demir-Çelik", "Otomotiv-Makine", "Lojistik", "Bilgi-İletişim", "Finans-Sigorta"])
                for i in range(3):
                    it = self.sec_ind.model().item(i)
                    if it: it.setCheckState(Qt.Checked)
            
                self.lbl_sec_per = QLabel("Dönem:")
                self.sec_start = QComboBox()
                self.sec_end = QComboBox()
            
                sec_top_h.addWidget(self.lbl_sec_c); sec_top_h.addWidget(self.sec_c)
                self.btn_clear_sec_c = QPushButton("🧹"); self.btn_clear_sec_c.setFixedWidth(30); self.btn_clear_sec_c.clicked.connect(self.sec_c.clearSelection); sec_top_h.addWidget(self.btn_clear_sec_c)
                sec_top_h.addWidget(self.lbl_sec_ind); sec_top_h.addWidget(self.sec_ind)
                self.btn_clear_sec_ind = QPushButton("🧹"); self.btn_clear_sec_ind.setFixedWidth(30); self.btn_clear_sec_ind.clicked.connect(self.sec_ind.clearSelection); sec_top_h.addWidget(self.btn_clear_sec_ind)
                sec_top_h.addWidget(self.lbl_sec_per); sec_top_h.addWidget(self.sec_start); sec_top_h.addWidget(QLabel("-")); sec_top_h.addWidget(self.sec_end)
                sec_top_h.addStretch()
                p7l.addLayout(sec_top_h)
            
                self.sec_web = QWebEngineView()
                _ssec = self.sec_web.settings()
                _ssec.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _ssec.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _ssec.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.sec_web.setHtml("<body style='background:#fafafa;'></body>")
                p7l.addWidget(self.sec_web)
            
                self.sec_narrative = QTextEdit(); self.sec_narrative.setReadOnly(True)
                self.sec_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#f4f9f4; border-left:5px solid #27ae60; font-family:'Segoe UI',sans-serif; font-size:12px;")
                self.sec_narrative.setFixedHeight(160)
                p7l.addWidget(self.sec_narrative)
                self.stacked_widget.addWidget(page7)

                # PAGE 8 (Risk Analizi)
                page8 = QWidget(); p8l = QVBoxLayout(page8)
                risk_top_h = QHBoxLayout()
            
                self.lbl_risk_c = QLabel("Ülke/Bölge:")
                self.risk_c = CheckableComboBox()
            
                self.lbl_risk_ind = QLabel("Gösterge:")
                self.risk_ind = CheckableComboBox()
            
                self.lbl_risk_per = QLabel("Dönem:")
                self.risk_start = QComboBox()
                self.risk_end = QComboBox()
            
                risk_top_h.addWidget(self.lbl_risk_c); risk_top_h.addWidget(self.risk_c)
                self.btn_clear_risk_c = QPushButton("🧹"); self.btn_clear_risk_c.setFixedWidth(30); self.btn_clear_risk_c.clicked.connect(self.risk_c.clearSelection); risk_top_h.addWidget(self.btn_clear_risk_c)
                risk_top_h.addWidget(self.lbl_risk_ind); risk_top_h.addWidget(self.risk_ind)
                self.btn_clear_risk_ind = QPushButton("🧹"); self.btn_clear_risk_ind.setFixedWidth(30); self.btn_clear_risk_ind.clicked.connect(self.risk_ind.clearSelection); risk_top_h.addWidget(self.btn_clear_risk_ind)
                risk_top_h.addWidget(self.lbl_risk_per); risk_top_h.addWidget(self.risk_start); risk_top_h.addWidget(QLabel("-")); risk_top_h.addWidget(self.risk_end)
                risk_top_h.addStretch()
                p8l.addLayout(risk_top_h)
            
                self.risk_web = QWebEngineView()
                _srisk = self.risk_web.settings()
                _srisk.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _srisk.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _srisk.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.risk_web.setHtml("<body style='background:#fafafa;'></body>")
                p8l.addWidget(self.risk_web)
            
                self.risk_narrative = QTextEdit(); self.risk_narrative.setReadOnly(True)
                self.risk_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#fdf2f2; border-left:5px solid #e74c3c; font-family:'Segoe UI',sans-serif; font-size:12px;")
                self.risk_narrative.setFixedHeight(160)
                p8l.addWidget(self.risk_narrative)
                self.stacked_widget.addWidget(page8)
                # PAGE 9 (Korelasyon)
                page9 = QWidget(); p9l = QVBoxLayout(page9)
                corr_top_h = QHBoxLayout()
            
                self.lbl_corr_x = QLabel("X Ekseni:")
                self.corr_x = QComboBox()
                self.lbl_corr_y = QLabel("Y Ekseni:")
                self.corr_y = QComboBox()
                self.lbl_corr_c = QLabel("Ülke/Bölge:")
                self.corr_c = CheckableComboBox()
            
                self.btn_corr_mode = QPushButton("📈 Dönem")
                self.btn_corr_mode.setFixedWidth(80)
                self.btn_corr_mode.setCheckable(True)
                self.btn_corr_mode.setChecked(True)
                self.btn_corr_mode.clicked.connect(self.toggle_corr_mode)
            
                self.lbl_corr_per = QLabel("Dönem:")
                self.corr_start = QComboBox()
                self.corr_end = QComboBox()
                self.lbl_corr_per.setVisible(False)
                self.corr_start.setVisible(False)
                self.corr_end.setVisible(False)
            
                self.lbl_corr_year = QLabel("Yıl:")
                self.corr_year = QComboBox()
                self.lbl_corr_year.setVisible(True)
                self.corr_year.setVisible(True)
            
                self.chk_corr_trend = QCheckBox("Trend")
                self.chk_corr_color = QCheckBox("Bölgesel")
                self.chk_corr_color.setChecked(True)
            
                corr_top_h.addWidget(self.lbl_corr_x); corr_top_h.addWidget(self.corr_x)
                corr_top_h.addWidget(self.lbl_corr_y); corr_top_h.addWidget(self.corr_y)
                corr_top_h.addWidget(self.lbl_corr_c); corr_top_h.addWidget(self.corr_c)
                self.btn_clear_corr_c = QPushButton("🧹"); self.btn_clear_corr_c.setFixedWidth(30); self.btn_clear_corr_c.clicked.connect(self.corr_c.clearSelection); corr_top_h.addWidget(self.btn_clear_corr_c)
                corr_top_h.addWidget(self.btn_corr_mode)
                corr_top_h.addWidget(self.lbl_corr_per); corr_top_h.addWidget(self.corr_start); corr_top_h.addWidget(QLabel("-") if self.corr_mode=="period" else QLabel("")); corr_top_h.addWidget(self.corr_end)
                corr_top_h.addWidget(self.lbl_corr_year); corr_top_h.addWidget(self.corr_year)
                corr_top_h.addWidget(self.chk_corr_trend)
                corr_top_h.addWidget(self.chk_corr_color)
                corr_top_h.addStretch()
                p9l.addLayout(corr_top_h)
            
                self.corr_web = QWebEngineView()
                _scorr = self.corr_web.settings()
                _scorr.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                _scorr.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                _scorr.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                self.corr_web.setHtml("<body style='background:#fafafa;'></body>")
                p9l.addWidget(self.corr_web)
            
                self.corr_narrative = QTextEdit(); self.corr_narrative.setReadOnly(True)
                self.corr_narrative.setStyleSheet("padding:10px; border-radius:5px; background:#f4f4f9; border-left:5px solid #2980b9; font-family:'Segoe UI',sans-serif; font-size:12px;")
                self.corr_narrative.setFixedHeight(160)
                p9l.addWidget(self.corr_narrative)
                self.stacked_widget.addWidget(page9)
            
                # PAGE 10 (Enerji Ekonomisi)
                page10 = QWidget(); p10l = QVBoxLayout(page10)
                energy_top_h = QHBoxLayout()
                self.energy_country = CheckableComboBox()
                self.energy_start = QComboBox(); self.energy_start.addItems([str(y) for y in range(2000, 2026)]); self.energy_start.setCurrentText("2000")
                self.energy_end = QComboBox(); self.energy_end.addItems([str(y) for y in range(2000, 2026)]); self.energy_end.setCurrentText("2024")
                
                for c in [self.energy_country, self.energy_start, self.energy_end]:
                    c.currentTextChanged.connect(self.update_energy)
                
                self.lbl_energy_c = QLabel("Ülkeler:"); energy_top_h.addWidget(self.lbl_energy_c); energy_top_h.addWidget(self.energy_country)
                self.btn_clear_energy_c = QPushButton("🧹"); self.btn_clear_energy_c.setFixedWidth(30); self.btn_clear_energy_c.clicked.connect(self.energy_country.clearSelection); energy_top_h.addWidget(self.btn_clear_energy_c)
                self.lbl_energy_per = QLabel("Dönem:"); energy_top_h.addWidget(self.lbl_energy_per)
                energy_top_h.addWidget(self.energy_start); energy_top_h.addWidget(QLabel("–")); energy_top_h.addWidget(self.energy_end)
                energy_top_h.addStretch()
                self.btn_export_energy = QPushButton("📑 Rapor Al"); self.btn_export_energy.clicked.connect(self.export_energy_pdf)
                energy_top_h.addWidget(self.btn_export_energy)
                p10l.addLayout(energy_top_h)
                
                energy_charts_grid = QGridLayout()
                energy_charts_grid.setSpacing(8)
                
                self.energy_web1 = QWebEngineView()
                self.energy_web1.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                self.energy_web1.setHtml("<body style='background:#fafafa;'></body>")
                energy_charts_grid.addWidget(self.energy_web1, 0, 0)
                
                self.energy_web2 = QWebEngineView()
                self.energy_web2.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                self.energy_web2.setHtml("<body style='background:#fafafa;'></body>")
                energy_charts_grid.addWidget(self.energy_web2, 0, 1)
                
                self.energy_web3 = QWebEngineView()
                self.energy_web3.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                self.energy_web3.setHtml("<body style='background:#fafafa;'></body>")
                energy_charts_grid.addWidget(self.energy_web3, 1, 0, 1, 2)
                
                p10l.addLayout(energy_charts_grid)
                
                self.lbl_energy_sources = QLabel()
                self.lbl_energy_sources.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-top: 3px; padding: 3px; background-color: #f4f6f7; border-radius: 4px; border: 1px solid #d5dbdb;")
                self.lbl_energy_sources.setWordWrap(True)
                p10l.addWidget(self.lbl_energy_sources)
                
                self.stacked_widget.addWidget(page10)            
                for c in [self.corr_x, self.corr_y, self.corr_c, self.corr_start, self.corr_end, self.corr_year, self.chk_corr_trend, self.chk_corr_color]:
                    if hasattr(c, 'currentTextChanged'): c.currentTextChanged.connect(self.draw_corr_chart)
                    elif hasattr(c, 'stateChanged'): c.stateChanged.connect(self.draw_corr_chart)

                for c in [self.risk_c, self.risk_ind, self.risk_start, self.risk_end]:
                    c.currentTextChanged.connect(self.draw_risk_chart)
            
                for c in [self.sec_c, self.sec_ind, self.sec_start, self.sec_end]:
                    c.currentTextChanged.connect(self.draw_sectoral_chart)

            
                for c in [self.pub_c, self.pub_ind, self.pub_start, self.pub_end]:
                    c.currentTextChanged.connect(self.draw_pub_chart)
            
                self.indicator_metadata = {
                    'GSYİH': {
                        'tanim': 'Bir ekonomide belirli bir dönemde cari fiyatlarla üretilen nihai mal ve hizmetlerin toplam piyasa değeridir. Keynesyen çerçevede toplam talebin (efektif talep) hacmini yansıtır.',
                        'birim': '$',
                        'metodoloji': 'Cari Fiyatlar (Nominal). Fiyat hareketlerinden arındırılmamıştır. Küresel ölçekte yapısal ekonomik büyüklükleri ve kapasiteleri karşılaştırmak için referans alınır.',
                        'kod': 'NY.GDP.MKTP.CD'
                    },
                    'GSYİH (Reel)': {
                        'tanim': 'Enflasyon etkisinden arındırılmış, sabit baz yılı fiyatlarıyla ölçülen üretim hacmidir. Ekonominin üretken kapasitesindeki fiziksel ve reel artışı temsil eder.',
                        'birim': '$',
                        'metodoloji': 'Sabit 2015 Fiyatları (Reel). Hacimsel üretim artışlarını ölçer. Uzun dönemli kalkınma ve büyüme analizlerinde temel referans göstergesidir.',
                        'kod': 'NY.GDP.MKTP.KD'
                    },
                    'GSMH': ('Gayri Safi Milli Hasıla (Nominal)', 'Ülke vatandaşlarının yurtiçi ve yurtdışında ürettiği toplam değerdir.', 'World Bank (NY.GNP.MKTP.CD)'),
                    'GSMH (Reel)': ('Reel GSMH (2015 Sabit Fiyatlar)', 'Enflasyondan arındırılmış Gayri Safi Milli Hasıla.', 'World Bank (NY.GNP.MKTP.KD)'),
                    'Kişi Başı GSYİH': {
                        'tanim': 'Toplam nominal yurt içi hasılanın nüfusa bölünmesiyle elde edilen ortalama gelirdir. Kalkınma iktisadı perspektifinde; sınıf içi gelir dağılımı adaletsizliğini gizlediği için refahın tek başına yeterli bir ölçütü kabul edilmez.',
                        'birim': '$',
                        'metodoloji': 'Cari Fiyatlar (Nominal). Uluslararası refah karşılaştırmalarında mutlak surette (Satın Alma Gücü Paritesi - SAGP / PPP) vurgusu dikkate alınmalıdır.',
                        'kod': 'NY.GDP.PCAP.CD'
                    },
                    'Kişi Başı GSMH': ('Kişi Başı GSMH (Nominal)', 'Toplam nominal GSMH\'nin nüfusa bölünmesiyle elde edilen ortalama gelirdir.', 'World Bank (NY.GNP.PCAP.CD)'),
                    'Kişi Başı GSMH (Reel)': ('Kişi Başı GSMH (Reel)', 'Toplam reel GSMH\'nin nüfusa bölünmesiyle elde edilen ortalama gelirdir.', 'World Bank (NY.GNP.PCAP.KD)'),
                    'Kişi Başı GSYİH (Reel)': {
                        'tanim': 'Enflasyon etkisinden arındırılmış, sabit baz yılı fiyatlarıyla kişi başı ortalama gelir.',
                        'birim': '$ (2015 Sabit Fiyatlar)',
                        'metodoloji': 'World Bank (NY.GDP.PCAP.KD)'
                    },
                    'Kişi Başı Enerji (kWh)': {
                        'tanim': 'Kişi başı yıllık birincil enerji tüketimi.',
                        'birim': 'kWh',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Fosil Yakıt Payı (%)': {
                        'tanim': 'Toplam elektrik üretiminde fosil yakıtların yüzdesi.',
                        'birim': '%',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Yenilenebilir Payı (%)': {
                        'tanim': 'Toplam elektrik üretiminde yenilenebilir kaynakların yüzdesi.',
                        'birim': '%',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Karbon (Milyon Ton)': {
                        'tanim': 'Fosil yakıt kullanımı kaynaklı yıllık toplam CO2 emisyonu.',
                        'birim': 'Milyon Ton',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Kişi Başı Karbon (Ton)': {
                        'tanim': 'Kişi başına düşen yıllık ortalama CO2 emisyonu.',
                        'birim': 'Ton',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Kişi Başı Karbon (Ton)': {
                        'tanim': 'Kişi başına düşen yıllık ortalama CO2 emisyonu.',
                        'birim': 'Ton',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Enerji İthalatı Bağımlılığı': {
                        'tanim': 'Toplam enerji kullanımında net enerji ithalatının yüzdesidir. Negatif değerler net ihracatçıyı gösterir.',
                        'birim': '%',
                        'metodoloji': 'World Bank (EG.IMP.CONS.ZS)'
                    },
                    'VDem_Score': ('V-Dem Liberal Demokrasi Endeksi', 'Siyasi katılım, hukukun üstünlüğü ve sivil özgürlükler üzerinden ülke demokrasisini ölçer.', 'V-Dem Institute (v-dem.net | v2x_libdem)'),
                    'Kişi Başı GSYİH (SAGP)': ('Kişi Başı GSYİH (SAGP)', 'Satın alma gücü paritesine göre düzeltilmiş kişi başı GSYİH.', 'World Bank (NY.GDP.PCAP.PP.CD)'),
                    'Kişi Başı GSMH (SAGP)': ('Kişi Başı GSMH (SAGP)', 'Satın alma gücü paritesine göre düzeltilmiş kişi başı GSMH.', 'World Bank (NY.GNP.PCAP.PP.CD)'),
                    'Enflasyon': {
                        'tanim': 'Genel fiyat düzeyindeki sürekli artış eğilimidir. Gelir bölüşümünü bozucu etkisi ve sabit gelirlilerin (ücretlilerin) reel satın alma gücünü aşındırması bakımından kritik bir istikrarsızlık ve bölüşüm sorunudur.',
                        'birim': '%',
                        'metodoloji': 'Yıllık Değişim. Tüketici fiyat endeksindeki yıllık yüzde değişimdir. Sepet bazlı enflasyonu yansıtır.',
                        'kod': 'FP.CPI.TOTL.ZG'
                    },
                    'İşsizlik': {
                        'tanim': 'Sermaye birikimi yetersizliği ve efektif talep eksikliği sonucu ortaya çıkan; cari ücret düzeyinde çalışmaya hazır ve istekli olduğu halde istihdam edilemeyen atıl işgücü kapasitesidir.',
                        'birim': '% (İşgücüne Oran)',
                        'metodoloji': 'Dünya Bankası WDI (ILOSTAT)',
                        'kod': 'SL.UEM.TOTL.ZS'
                    },
                    'Büyüme': {
                        'tanim': 'Reel gayrisafi yurt içi hasılanın bir önceki yıla göre oransal artışıdır. İstihdam yaratma ve sermaye birikimi kapasitesindeki değişimi ölçer.',
                        'birim': '%',
                        'metodoloji': 'Yıllık Değişim. Sabit fiyatlar üzerinden hesaplanan büyüme oranıdır.',
                        'kod': 'NY.GDP.MKTP.KD.ZG'
                    },
                    'Cari Denge': {
                        'tanim': 'Bir ülkenin dış dünyayla olan ticari ve mali işlemlerinin (mal, hizmet, gelir transferleri) neticesidir. Kalkınmakta olan ülkelerde yapısal dışa bağımlılığın ve döviz darboğazının (foreign exchange constraint) başat göstergesidir.',
                        'birim': '%',
                        'metodoloji': 'Yoğunluk/Pay. Milli gelire oran (% GSYİH) olarak uluslararası sermaye hareketlerinin yönünü tayin eder.',
                        'kod': 'BN.CAB.XOKA.GD.ZS'
                    },
                    'Borç Oranı': ('Merkezi Yönetim Borcu (% GSYİH)', 'Devletin toplam borcunun milli gelire oranıdır.', 'World Bank (GC.DOD.TOTL.GD.ZS)'),
                    'Gini': {
                        'tanim': 'Gelir veya servet dağılımındaki adaletsizliğin temel istatistiksel ölçütüdür. Sınıfsal bölüşüm ilişkilerinin, toplumsal eşitsizliğin ve ekonomik refahın tabana yayılmamasının şiddetini yansıtır.',
                        'birim': 'Endeks Değeri',
                        'metodoloji': '0 değeri tam eşitliği, 100 değeri ise tüm gelirin tek bir kişide/zümrede toplandığı mutlak eşitsizliği ifade eder.',
                        'kod': 'SI.POV.GINI'
                    },
                    'Ar-Ge Yoğunluğu': {
                        'tanim': 'Teknolojik bağımlılığı kırma, sanayileşme ve içsel büyüme dinamiklerini güçlendirme amacıyla, inovasyon ve teknoloji üretimine tahsis edilen makroekonomik kaynakların payıdır.',
                        'birim': '% (GSYİH)',
                        'metodoloji': 'Dünya Bankası WDI',
                        'kod': 'GB.XPD.RSDV.GD.ZS'
                    },
                    'Genç İşsizlik': ('Genç İşsizlik Oranı (15-24 Yaş)', 'Genç nüfus içerisindeki işsizlik oranını ifade eder.', 'World Bank (SL.UEM.1524.ZS)'),
                    'Karbon': ('Kişi Başı Karbon Salınımı', 'Kişi başına düşen metrik ton cinsinden karbondioksit emisyonudur.', 'World Bank (EN.ATM.CO2E.PC)'),
                    'Yaşam Süresi': ('Doğuşta Beklenen Yaşam Süresi', 'Yeni doğan bir bireyin mevcut ölüm oranlarına göre beklenen ortalama ömrüdür.', 'World Bank (SP.DYN.LE00.IN)'),
                    'Eğitim': ('Eğitim Harcamaları (% GSYİH)', 'Kamu eğitim harcamalarının toplam milli gelire oranıdır.', 'World Bank (SE.XPD.TOTL.GD.ZS)'),
                    'Sağlık': ('Sağlık Harcamaları (% GSYİH)', 'Kamu ve özel sağlık harcamalarının toplam milli gelire oranıdır.', 'World Bank (SH.XPD.CHEX.GD.ZS)'),
                    'İmalat': ('İmalat Sanayi (% GSYİH)', 'İmalat sanayi üretiminin milli gelir içindeki payıdır.', 'World Bank (NV.IND.MANF.ZS)'),
                    'Enerji-Maden': ('Doğal Kaynak Rantı (% GSYİH)', 'Petrol, doğalgaz, kömür ve madenlerden elde edilen toplam rantın milli gelire oranıdır.', 'World Bank (NY.GDP.TOTL.RT.ZS)'),
                    'Demir-Çelik': ('Metal ve Maden İhracatı (% Mal İhracı)', 'Demir-çelik ve diğer metal cevherlerinin toplam mal ihracatı içindeki payıdır.', 'World Bank (TX.VAL.MMTL.ZS.UN)'),
                    'Otomotiv-Makine': ('Ulaşım ve Makine (% İmalat)', 'Ulaşım araçları ve makine üretiminin toplam imalat katma değeri içindeki payıdır.', 'World Bank (NV.MNF.MTRN.ZS.UN)'),
                    'Lojistik': ('Lojistik ve Ulaşım (% Hizmet İhracı)', 'Ulaştırma ve lojistik hizmetlerinin toplam ticari hizmet ihracatı içindeki payıdır.', 'World Bank (TX.VAL.TRAN.ZS.WT)'),
                    'İletişim-ICT': ('Bilgi ve İletişim (% Hizmet İhracı)', 'Bilişim ve iletişim teknolojileri hizmetlerinin toplam hizmet ihracatı içindeki payıdır.', 'World Bank (BX.GSR.CCIS.ZS)'),
                    'Finans-Sigorta': ('Finans ve Sigorta (% Hizmet İhracı)', 'Finansal hizmetler ve sigortacılık faaliyetlerinin toplam hizmet ihracatı içindeki payıdır.', 'World Bank (BX.GSR.INSF.ZS)'),
                    'Cari Açık': ('Cari İşlemler Dengesi (% GSYİH)', 'Cari açık veya fazlanın milli gelire oranıdır. Dış denge performansını yansıtır.', 'World Bank (BN.CAB.XOKA.GD.ZS)'),
                    'Dış Borç-GNI': ('Toplam Dış Borç Stoku (% GSMH)', 'Ülkenin toplam dış borç yükünün Gayri Safi Milli Hasılaya oranıdır.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
                    'Risk Primi': ('Ülke Risk Primi (Proxy)', 'Borçlanma faiz oranı ile hazine bonosu faizi arasındaki farktır. CDS muadili risk göstergesidir.', 'World Bank (FR.INR.RISK)'),
                    'İthalat Karşılama': ('İthalat Karşılama Süresi (Ay)', 'Toplam rezervlerin mevcut ithalat hacmini kaç ay boyunca karşılayabileceğini gösterir.', 'World Bank (FI.RES.TOTL.MO)'),
                    'Kısa Vadeli Borç': ('Kısa Vadeli Dış Borç / Toplam Rezervler', 'Bir yıl içinde ödenecek dış borcun merkez bankası rezervlerine oranıdır.', 'World Bank (DT.DOD.DSTC.IR.ZS)'),
                    'DYY-Girişi': ('Doğrudan Yabancı Yatırımlar (% GSYİH)', 'Net yabancı sermaye girişinin milli gelir içindeki payıdır.', 'World Bank (BX.KLT.DINV.WD.GD.ZS)'),
                    'REK': ('Reel Efektif Döviz Kuru (REER)', 'Tüketici fiyatlarına göre düzeltilmiş, ticaret ağırlıklı nominal kur endeksidir (2010=100).', 'World Bank (PX.REX.REER)'),
                    'Reel Faiz': ('Reel Faiz Oranı (%)', 'Enflasyondan arındırılmış piyasa faiz oranıdır.', 'World Bank (FR.INR.RINR)'),
                    'Bütçe Dengesi': ('Bütçe Dengesi (% GSYİH)', 'Merkezi yönetim bütçe açığının veya fazlasının GSYİH içindeki payıdır.', 'World Bank (GC.NLD.TOTL.GD.ZS)'),
                    'Borç Servisi': ('Toplam Borç Servisi (% İhracat)', 'Anapara ve faiz ödemelerinin toplam mal ve hizmet ihracatına oranıdır.', 'World Bank (DT.TDS.DECT.EX.ZS)'),
                    'İnsani Gelişmişlik': ('İnsani Sermaye Endeksi', 'Bir ülkenin sağlık ve eğitim verilerine dayanarak gelecekteki verimliliğini ölçer.', 'World Bank (HD.HCI.OVRL)'),
                    'Yoksulluk': ('Yoksulluk Sınırı', 'Günde belirli bir tutarın altında yaşayan nüfusun yüzdesidir.', 'World Bank (SI.POV.DDAY)'),
                    'İhracat': {
                        'tanim': 'Bir ülkenin yerleşik kişi ve kurumları tarafından dış dünyaya satılan mal ve hizmetlerin toplam değeri.',
                        'birim': 'GSYİH İçindeki Payı (%)',
                        'metodoloji': 'Ödemeler dengesi istatistiklerine göre kaydedilen toplam mal ve hizmet ihracat gelirlerinin GSYİH\'ye oranıdır. Ekonominin dışa açıklık derecesini ve uluslararası rekabet gücünü yansıtır.',
                        'kod': 'NE.EXP.GNFS.ZS'
                    },
                    'İthalat': {
                        'tanim': 'Dış dünyadan yerleşik kişi veya kurumlara satılan (ülkeye giren) mal ve hizmetlerin toplam değeri.',
                        'birim': 'GSYİH İçindeki Payı (%)',
                        'metodoloji': 'Toplam ithalat harcamalarının GSYİH\'ye oranıdır. Üretimin ithal ara malı ve enerjiye bağımlılığını ile iç talebin ithal tüketim eğilimini (yapısal dış ticaret açığı riskini) yansıtır.',
                        'kod': 'NE.IMP.GNFS.ZS'
                    },
                    'Tarım': ('Tarım Sektörü (% GSYİH)', 'Tarım, ormancılık ve balıkçılık sektörlerinin toplam katma değeridir.', 'World Bank (NV.AGR.TOTL.ZS)'),
                    'Sanayi': ('Sanayi Sektörü (% GSYİH)', 'İmalat ve inşaat dahil tüm sanayi kollarının toplam katma değeridir.', 'World Bank (NV.IND.TOTL.ZS)'),
                    'Hizmetler': ('Hizmetler Sektörü (% GSYİH)', 'Toptan, perakende, finans ve kamu hizmetlerinin katma değeridir.', 'World Bank (NV.SRV.TOTL.ZS)'),
                    'HDI_UNDP': {
                        'tanim': 'Ekonomik büyüme dogmasına karşı, insan merkezli bir kalkınma anlayışıyla ortalama yaşam süresi, eğitim erişimi ve insana yaraşır yaşam standardını ölçen bileşik endeks.',
                        'birim': 'Endeks Skoru (0 - 1 Skalası)',
                        'metodoloji': 'Birleşmiş Milletler Kalkınma Programı (UNDP) tarafından; doğuşta beklenen yaşam süresi, beklenen/ortalama öğrenim süresi ve SGP\'ye göre kişi başına düşen GSMH göstergelerinin geometrik ortalaması alınarak hesaplanır.',
                        'kod': 'UNDP-HDI'
                    },
                    'IHDI': ('Eşitsizliğe Uyarlanmış İnsani Gelişme Endeksi (IHDI)', 'HDI\'nin gelir, sağlık ve eğitim eşitsizliği ile düzültilmiş versiyonu. HDI ile IHDI arasındaki fark eşitsizlik kaybını gösterir.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'PHDI': ('Gezegensel Baskılara Uyarlanmış İnsani Gelişme Endeksi (PHDI)', 'HDI\'nin karbon salınımı ve malzeme ayağı ile düzültilmiş hali. Çevresel sürdürülebilirliği (ölcsür.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'GII': {
                        'tanim': 'Kadınların üreme sağlığı, siyasi/ekonomik güçlendirme ve işgücü piyasasına katılımları açısından maruz kaldıkları yapısal dezavantajları ve asimetrik toplumsal ilişkileri ölçen kompozit endekstir.',
                        'birim': 'Endeks Değeri',
                        'metodoloji': 'Teknik Not: 0 değeri mutlak tam eşitliği, 1 değeri ise mutlak tam eşitsizliği ifade eder.',
                        'kod': 'UNDP Human Development Report (hdr.undp.org)'
                    },
                    'GDI': ('Toplumsal Cinsiyet Gelişimi Endeksi (GDI)', 'Kadın ve erkek HDI değerlerinin oranıdır. 1.0=tam eşitlik; 1’den uzaklaşma eşitsizliği gösterir.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'VDem_Score': ('V-Dem Liberal Demokrasi Endeksi', 'Siyasi katılım, hukukun üstünlüğü ve sivil özgürlükler üzerinden ülke demokrasisini ölçer. 0=tam otoriter, 1=tam liberal demokrasi.', 'V-Dem Institute (v-dem.net | v2x_libdem)'),
                    'palma_ratio': {
                        'tanim': 'Nüfusun en zengin %10\'luk kesiminin toplam gelirden aldığı payın, en yoksul %40\'lık kesimin aldığı paya oranı.',
                        'birim': 'Oransal Katsayı',
                        'metodoloji': 'Kalkınma iktisadı perspektifiyle, orta sınıfın gelir payının görece sabit olduğu ampirik bulgusuna dayanır. Eşitsizliğin temel kaynağı olan uçlardaki (en zengin ile en yoksul arasındaki) bölüşüm krizini daha net ölçer.',
                        'kod': 'WIID / SWIID Derived'
                    },
                    'WIID_Ratio': ('WIID S10/S1 Gelir Oranı', 'Nüfusun en zengin %10\'u ile en yoksul %10\'u arasındaki gelir payı oranıdır. Değer yükseldikçe gelir eşitsizliği artar.', 'Dünya Bankası (SI.DST.10TH.10 / SI.DST.FRST.10)'),
                    'Kamu Harcamaları': ('Kamu Harcamaları (% GSYİH)', 'Genel hükümet tüketim harcamalarının milli gelire oranıdır.', 'World Bank (NE.CON.GOVT.ZS)'),
                    'Savunma Harcamaları': ('Savunma/Askeri Harcamalar (% GSYİH)', 'Silahlı kuvvetler için yapılan toplam kamu harcamasının milli gelire oranıdır.', 'World Bank (MS.MIL.XPND.GD.ZS)'),
                    'Vergi Gelirleri': ('Vergi Gelirleri (% GSYİH)', 'Devletin zorunlu kıldığı vergi toplamının milli gelire oranıdır.', 'World Bank (GC.TAX.TOTL.GD.ZS)'),
                    'Bütçe Dengesi': ('Merkezi Yönetim Bütçe Dengesi (% GSYİH)', 'Kamu gelirlerinin giderlerden farkının milli gelire oranıdır. Negatif değer açık anlamına gelir.', 'World Bank (GC.NLD.TOTL.GD.ZS)'),
                    'Sosyal Refah': ('Sosyal Koruma Kapsamı (Nüfus %)', 'Herhangi bir sosyal koruma programından yararlanan nüfusun yüzdesidir.', 'Dünya Bankası ASPIRE Programı (per_lm_all2.ad_pop_tot)'),
                    'Dış Borç': ('Dış Borç (% GSMH)', 'Yabancı alacaklılara olan toplam dış borç stökünün gayri safi milli hasılaya oranıdır.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
                    'IPI': ('Sanayi Üretim Endeksi (IPI)', 'Sanayi sektöründeki üretim hacminin değişimini ölçen endekstir.', 'Uygulama İçin Tanımlanmamış (Yerel Hesaplama)'),
                    'PPI': ('Üretici Fiyat Endeksi (ÜFE / PPI)', 'Üreticilerin sattığı ürünlerin fiyat değişimini ölçen endekstir.', 'Uygulama İçin Tanımlanmamış (Yerel Hesaplama)'),
                    'CDS': {
                        'tanim': 'Bir ülkenin borç yükümlülüklerini (egemen tahvillerini) temerrüde düşme (ödeyememe) riskine karşı sigortalamak için yatırımcının ödediği yıllık risk primi.',
                        'birim': 'Baz Puan (bps) - 100 bps = %1',
                        'metodoloji': 'Tezgah altı piyasalarda arz-talebe göre belirlenen türev ürün fiyatlamasıdır. Ülkenin makroekonomik kırılganlığına, döviz rezerv yeterliliğine ve dış borç çevirme kapasitesine dair uluslararası piyasa algısını yansıtır.',
                        'kod': 'Market Data (Mkt)'
                    }
                }
            
                self.indicator_metadata_en = {
                    'GSYİH': ('Gross Domestic Product (Nominal)', 'The total market value of all final goods and services produced within a country.', 'World Bank (NY.GDP.MKTP.CD)'),
                    'GSYİH (Reel)': {
                        'tanim': 'The inflation-adjusted, volumetric market value of all final goods and services produced within a country during a specific period.',
                        'birim': 'Constant US Dollars (Billions $)',
                        'metodoloji': 'Calculated by deflating the Nominal GDP using the GDP Implicit Deflator to base year prices (2015 for WB). It is the primary measure of economic growth.',
                        'kod': 'NY.GDP.MKTP.KD'
                    },
                    'GSMH': ('Gross National Income (Nominal)', 'The total value produced by a country\'s citizens both domestically and internationally.', 'World Bank (NY.GNP.MKTP.CD)'),
                    'GSMH (Reel)': ('Real GNI (2015 Constant Prices)', 'Inflation-adjusted volumetric Gross National Income.', 'World Bank (NY.GNP.MKTP.KD)'),
                    'Kişi Başı GSYİH': {
                        'tanim': 'An indicator of average welfare, calculated by dividing the total nominal gross domestic product of a country by its mid-year demographic population.',
                        'birim': 'US Dollars (Current Prices)',
                        'metodoloji': 'Calculated using the formula [Total Nominal GDP / Mid-Year Population]. Since it masks distributional relations, class differences, and income inequality, it cannot be considered a sole measure of "development".',
                        'kod': 'NY.GDP.PCAP.CD'
                    },
                    'Kişi Başı GSMH': ('GNI Per Capita', 'The average income obtained by dividing total GNI by the population.', 'World Bank (NY.GNP.PCAP.CD)'),
                    'Kişi Başı GSMH (Reel)': ('Real GNI Per Capita', 'Inflation-adjusted average income obtained by dividing total GNI by the population.', 'World Bank (NY.GNP.PCAP.KD)'),
                    'Kişi Başı GSYİH (Reel)': {
                        'tanim': 'Inflation-adjusted average per capita income at constant base year prices.',
                        'birim': '$ (2015 Constant Prices)',
                        'metodoloji': 'World Bank (NY.GDP.PCAP.KD)'
                    },
                    'Kişi Başı Enerji (kWh)': {
                        'tanim': 'Annual primary energy consumption per capita.',
                        'birim': 'kWh',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Fosil Yakıt Payı (%)': {
                        'tanim': 'Share of fossil fuels in total electricity generation.',
                        'birim': '%',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Yenilenebilir Payı (%)': {
                        'tanim': 'Share of renewables in total electricity generation.',
                        'birim': '%',
                        'metodoloji': 'Our World in Data (Energy)'
                    },
                    'Karbon (Milyon Ton)': {
                        'tanim': 'Annual total CO2 emissions from fossil fuels.',
                        'birim': 'Million Tonnes',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Kişi Başı Karbon (Ton)': {
                        'tanim': 'Average annual CO2 emissions per capita.',
                        'birim': 'Tonnes',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Kişi Başı Karbon (Ton)': {
                        'tanim': 'Average annual CO2 emissions per capita.',
                        'birim': 'Tonnes',
                        'metodoloji': 'Our World in Data (CO2)'
                    },
                    'Enerji İthalatı Bağımlılığı': {
                        'tanim': 'Net energy imports as a percentage of energy use. Negative values indicate net exporters.',
                        'birim': '%',
                        'metodoloji': 'World Bank (EG.IMP.CONS.ZS)'
                    },
                    'VDem_Score': ('V-Dem Liberal Democracy Index', 'Measures country democracy based on political participation, rule of law, and civil liberties.', 'V-Dem Institute (v-dem.net | v2x_libdem)'),
                    'Kişi Başı GSYİH (SAGP)': ('GDP Per Capita (PPP)', 'GDP per capita based on purchasing power parity (PPP).', 'World Bank (NY.GDP.PCAP.PP.CD)'),
                    'Kişi Başı GSMH (SAGP)': ('GNI Per Capita (PPP)', 'GNI per capita based on purchasing power parity (PPP).', 'World Bank (NY.GNP.PCAP.PP.CD)'),
                    'Enflasyon': {
                        'tanim': 'The annual average rate of increase in the general price level of a representative basket of basic goods and services purchased by households.',
                        'birim': 'Annual Percentage Change (%)',
                        'metodoloji': 'Based on the Laspeyres index logic, it is the proportional change of a weighted standard price basket (CPI) compared to the same period of the previous year. (Note: Not measured as a ratio to GDP).',
                        'kod': 'FP.CPI.TOTL.ZG'
                    },
                    'Ar-Ge Harcaması': ('R&D Expenditure (% GDP)', 'The ratio of resources allocated to research and development activities to national income.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'Ar-Ge Yoğunluğu': ('R&D Intensity (% GDP)', 'The share of macroeconomic resources allocated to innovation and technology production as a percentage of GDP.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'ArGe_Harcaması': ('R&D Intensity (% GDP)', 'The share of resources dedicated to research and development as a percentage of GDP.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'İşsizlik': {
                        'tanim': 'The share of individuals in the total labor force who are not employed during the reference period, are actively seeking work, and are available for work (age 15+).',
                        'birim': 'Percentage Share in Labor Force (%)',
                        'metodoloji': 'World Bank WDI (ILOSTAT)',
                        'kod': 'SL.UEM.TOTL.ZS'
                    },
                    'Büyüme': ('Real GDP Growth Rate', 'Refers to the real volumetric growth of the economy compared to the previous year.', 'World Bank (NY.GDP.MKTP.KD.ZG)'),
                    'Cari Denge': {
                        'tanim': 'The net balance of a country\'s transactions with the rest of the world, including goods, services, primary income (wages/investment returns), and secondary income (current transfers).',
                        'birim': 'Share in GDP (%)',
                        'metodoloji': 'The sum of the balance of trade, balance of services, and net income from abroad. A negative value (Current Account Deficit) indicates that domestic savings are insufficient to cover investments, requiring net external financing (borrowing).',
                        'kod': 'BN.CAB.XOKA.GD.ZS'
                    },
                    'Borç Oranı': ('Central Government Debt (% GDP)', 'The ratio of the government\'s total debt to national income.', 'World Bank (GC.DOD.TOTL.GD.ZS)'),
                    'Gini': {
                        'tanim': 'A statistical measure of the degree of inequality in the distribution of family income (or wealth) within an economy.',
                        'birim': 'Coefficient (0 - 100 Scale)',
                        'metodoloji': 'The ratio of the area between the Lorenz curve and the line of absolute equality to the total area under the line of absolute equality. 0 represents perfect equality, while 100 represents perfect inequality (all income concentrated in one person).',
                        'kod': 'SI.POV.GINI'
                    },
                    'Ar-Ge Harcaması': ('R&D Expenditure (% GDP)', 'The ratio of resources allocated to research and development activities to national income.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'Ar-Ge Yoğunluğu': ('R&D Intensity (% GDP)', 'The share of macroeconomic resources allocated to innovation and technology production as a percentage of GDP.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'ArGe_Harcaması': ('R&D Intensity (% GDP)', 'The share of resources dedicated to research and development as a percentage of GDP.', 'World Bank (GB.XPD.RSDV.GD.ZS)'),
                    'Genç İşsizlik': ('Youth Unemployment Rate (Ages 15-24)', 'Expresses the unemployment rate among the young population.', 'World Bank (SL.UEM.1524.ZS)'),
                    'Karbon': ('Carbon Emissions Per Capita', 'Carbon dioxide emissions in metric tons per capita.', 'World Bank (EN.ATM.CO2E.PC)'),
                    'Yaşam Süresi': ('Life Expectancy at Birth', 'The average expected lifespan of a newborn based on current mortality rates.', 'World Bank (SP.DYN.LE00.IN)'),
                    'Eğitim': ('Education Expenditure (% GDP)', 'The ratio of public education expenditures to total national income.', 'World Bank (SE.XPD.TOTL.GD.ZS)'),
                    'Sağlık': ('Health Expenditure (% GDP)', 'The ratio of public and private health expenditures to total national income.', 'World Bank (SH.XPD.CHEX.GD.ZS)'),
                    'İmalat': ('Manufacturing (% GDP)', 'Value added of the manufacturing sector as a share of GDP.', 'World Bank (NV.IND.MANF.ZS)'),
                    'Enerji-Maden': ('Natural Resource Rents (% GDP)', 'Total rents from oil, gas, coal, and minerals as a percentage of GDP.', 'World Bank (NY.GDP.TOTL.RT.ZS)'),
                    'Demir-Çelik': ('Ores and Metals Export (% Merch.)', 'Share of iron, steel, and other metal ores in total merchandise exports.', 'World Bank (TX.VAL.MMTL.ZS.UN)'),
                    'Otomotiv-Makine': ('Transport & Machinery (% Manuf.)', 'Share of transport equipment and machinery in total manufacturing value added.', 'World Bank (NV.MNF.MTRN.ZS.UN)'),
                    'Lojistik': ('Logistics & Transport (% Srv. Exp.)', 'Share of transport and logistics services in total commercial service exports.', 'World Bank (TX.VAL.TRAN.ZS.WT)'),
                    'İletişim-ICT': ('ICT Services (% Srv. Exp.)', 'Share of ICT services in total commercial service exports.', 'World Bank (BX.GSR.CCIS.ZS)'),
                    'Finans-Sigorta': ('Finance & Insurance (% Srv. Exp.)', 'Share of financial and insurance services in total commercial service exports.', 'World Bank (BX.GSR.INSF.ZS)'),
                    'Cari Açık': ('Current Account Balance (% GDP)', 'Current account balance as a share of GDP. Reflects external balance.', 'World Bank (BN.CAB.XOKA.GD.ZS)'),
                    'Dış Borç-GNI': ('External Debt Stock (% GNI)', 'Total external debt stocks as a percentage of Gross National Income.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
                    'Risk Primi': ('Risk Premium (Proxy)', 'The difference between the lending rate and the treasury bill rate.', 'World Bank (FR.INR.RISK)'),
                    'İthalat Karşılama': ('Import Cover (Months)', 'Total reserves in months of current merchandise imports.', 'World Bank (FI.RES.TOTL.MO)'),
                    'Kısa Vadeli Borç': ('Short-term Debt / Reserves (%)', 'Short-term external debt as a percentage of total reserves.', 'World Bank (DT.DOD.DSTC.IR.ZS)'),
                    'DYY-Girişi': ('FDI Inflows (% GDP)', 'Net foreign direct investment inflows as a percentage of GDP.', 'World Bank (BX.KLT.DINV.WD.GD.ZS)'),
                    'REK': ('Real Effective Exchange Rate (REER)', 'Consumer price-based index of the real value of currency (2010=100).', 'World Bank (PX.REX.REER)'),
                    'Reel Faiz': ('Real Interest Rate (%)', 'Lending interest rate adjusted for inflation as measured by the GDP deflator.', 'World Bank (FR.INR.RINR)'),
                    'Bütçe Dengesi': ('Budget Balance (% GDP)', 'Net lending/borrowing as a percentage of GDP.', 'World Bank (GC.NLD.TOTL.GD.ZS)'),
                    'Borç Servisi': ('Total Debt Service (% Exports)', 'Ratio of debt service to exports of goods, services, and primary income.', 'World Bank (DT.TDS.DECT.EX.ZS)'),
                    'İnsani Gelişmişlik': ('Human Capital Index', 'Measures a country\'s future productivity based on health and education data.', 'World Bank (HD.HCI.OVRL)'),
                    'Yoksulluk': ('Poverty Headcount Ratio', 'The percentage of the population living below a certain daily amount.', 'World Bank (SI.POV.DDAY)'),
                    'İhracat': {
                        'tanim': 'The total value of goods and services sold to the rest of the world by a country\'s resident individuals and institutions.',
                        'birim': 'Share in GDP (%)',
                        'metodoloji': 'The ratio of total exports of goods and services recorded in the balance of payments to the country\'s GDP. It reflects the degree of the economy\'s openness and its international competitiveness.',
                        'kod': 'NE.EXP.GNFS.ZS'
                    },
                    'İthalat': {
                        'tanim': 'The total value of goods and services purchased from the rest of the world by resident individuals or institutions.',
                        'birim': 'Share in GDP (%)',
                        'metodoloji': 'The ratio of total import expenditures to GDP. It reflects the production\'s dependence on imported intermediate goods/energy and domestic demand\'s propensity for imported consumption (structural foreign trade deficit risk).',
                        'kod': 'NE.IMP.GNFS.ZS'
                    },
                    'Tarım': ('Agriculture Sector (% GDP)', 'The total value added of agriculture, forestry, and fishing sectors.', 'World Bank (NV.AGR.TOTL.ZS)'),
                    'Sanayi': ('Industry Sector (% GDP)', 'The total value added of all industrial branches including manufacturing and construction.', 'World Bank (NV.IND.TOTL.ZS)'),
                    'Hizmetler': ('Services Sector (% GDP)', 'The value added of wholesale, retail, finance, and public services.', 'World Bank (NV.SRV.TOTL.ZS)'),
                    'HDI_UNDP': {
                        'tanim': 'A composite index measuring average achievement in key dimensions of human development: a long and healthy life, being knowledgeable, and having a decent standard of living.',
                        'birim': 'Index Score (0 - 1 Scale)',
                        'metodoloji': 'Calculated by the United Nations Development Programme (UNDP) as the geometric mean of normalized indices for life expectancy at birth, expected and mean years of schooling, and GNI per capita based on PPP.',
                        'kod': 'UNDP-HDI'
                    },
                    'IHDI': ('Inequality-adjusted HDI (IHDI)', 'HDI discounted for inequality in health, education and income. The gap between HDI and IHDI shows the inequality loss.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'PHDI': ('Planetary Pressures-adjusted HDI (PHDI)', 'HDI adjusted for per-capita carbon emissions and material footprint, reflecting environmental sustainability.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'GII': ('Gender Inequality Index (GII)', 'Measures gender inequalities in reproductive health, empowerment and labor market participation. 0=equality, 1=full inequality.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'GDI': ('Gender Development Index (GDI)', 'Ratio of female to male HDI. 1.0=full equality; deviation indicates gender disparity.', 'UNDP Human Development Report (hdr.undp.org)'),
                    'VDem_Score': ('V-Dem Liberal Democracy Index', 'Measures country democracy through political participation, rule of law, and civil liberties. 0=autocracy, 1=liberal democracy.', 'V-Dem Institute (v-dem.net | v2x_libdem)'),
                    'palma_ratio': {
                        'tanim': 'The ratio of the national income share of the richest 10% of the population to the share of the poorest 40%.',
                        'birim': 'Proportional Ratio',
                        'metodoloji': 'Based on the empirical finding in development economics that the middle class income share is relatively stable. It provides a clearer measure of the distributional crisis at the extremes (the richest vs. the poorest), which is the primary source of inequality.',
                        'kod': 'WIID / SWIID Derived'
                    },
                    'WIID_Ratio': ('WIID S10/S1 Income Ratio', 'Ratio of the income share of the top 10% to the bottom 10% of the population. Higher values indicate greater income inequality.', 'World Bank (SI.DST.10TH.10 / SI.DST.FRST.10)'),
                    'Kamu Harcamaları': ('General Government Expenditure (% GDP)', 'Ratio of general government consumption expenditure to national income.', 'World Bank (NE.CON.GOVT.ZS)'),
                    'Savunma Harcamaları': ('Military Expenditure (% GDP)', 'Total public expenditure on armed forces as a share of national income.', 'World Bank (MS.MIL.XPND.GD.ZS)'),
                    'Vergi Gelirleri': ('Tax Revenue (% GDP)', 'Ratio of compulsory tax revenues collected by the government to national income.', 'World Bank (GC.TAX.TOTL.GD.ZS)'),
                    'Bütçe Dengesi': ('Central Government Budget Balance (% GDP)', 'Difference between public revenues and expenditures as a share of GDP. Negative = deficit.', 'World Bank (GC.NLD.TOTL.GD.ZS)'),
                    'Sosyal Refah': ('Social Protection Coverage (% of Population)', 'Percentage of the population benefiting from at least one social protection program.', 'World Bank ASPIRE Program (per_lm_all2.ad_pop_tot)'),
                    'Dış Borç': ('External Debt (% GNI)', 'Total external debt stock owed to foreign creditors as a share of gross national income.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
                    'IPI': ('Industrial Production Index (IPI)', 'Index measuring the change in production volume in the industrial sector.', 'Not defined for this application (Local Calculation)'),
                    'PPI': ('Producer Price Index (PPI)', 'Index measuring the change in prices of goods sold by producers.', 'Not defined for this application (Local Calculation)'),
                    'CDS': {
                        'tanim': 'The annual risk premium paid by an investor to insure against the risk of a country defaulting on its debt obligations (sovereign bonds).',
                        'birim': 'Basis Points (bps) - 100 bps = 1%',
                        'metodoloji': 'Pricing of a derivative product determined by supply and demand in over-the-counter markets. It directly reflects international market perception of a country\'s macroeconomic fragility, foreign exchange reserve adequacy, and external debt rollover capacity.',
                        'kod': 'Market Data (Mkt)'
                    },
                    'Enerji İthalatı Bağımlılığı': {
                        'tanim': 'Energy imports, net (% of energy use). Negative values indicate net exporter.',
                        'birim': '%',
                        'metodoloji': 'World Bank (EG.IMP.CONS.ZS)'
                    }
                }
            
            
                # i18n dictionaries
                self.current_lang = 'tr'
                self.macro_mode = 'period'
                self.pub_mode = 'period'
                self.langs = {
                    'tr': {
                        'title': 'SBF Makro Veri Analiz Merkezi', 'logo': '🏛️ SBF\nMAKRO TERMİNAL',
                        'update_btn': '🌐 Verileri Güncelle', 'nav_map': '🏠 Genel Harita', 'nav_macro': '📊 Makroekonomi', 'nav_rank': '📊 Küresel Sıralama',
                        'nav_ts': '📈 Zaman Serisi Anlz.', 'nav_rd': '🌱 Kalkınma ve Bölüşüm', 'nav_pub': '🏛️ Kamu Maliyesi',
                        'nav_block': '📊 Küresel Sıralamalar', 'nav_bench': '🏁 Ülke Kıyaslama', 'nav_sector': '🏗️ Sektörel Paylar', 'nav_risk': '⚠️ Risk Analizi', 'nav_corr': '🔗 Korelasyon', 'nav_energy': '⚡ Enerji Ekonomisi',
                        'theme_dark': '🌙 Karanlık Mod', 'theme_light': '☀️ Aydınlık Mod',
                        'search_placeholder': '🔍 Ülke Seçin veya Arayın...', 'statik_yil': 'Statik Analiz Yılı:',
                        'refresh_btn': 'Anlık Yenile', 'clear_btn': 'Ekranı Temizle', 'copy_btn': '📋 Tüm Verileri Kopyala',
                        'mode_instant': '📍 Anlık', 'mode_period': '📅 Dönem',
                        'rank_title': '📊 KÜRESEL EKONOMİK HASILA SIRALAMASI', 'yil_sec': 'Yıl Seçiniz:',
                        'country_lbl': 'Ülke:', 'country1_lbl': 'Ülke 1:', 'country2_lbl': 'Ülke 2:',
                        'ind_lbl': 'Gösterge:', 'ind_sel_lbl': 'Gösterge:', 'period_lbl': 'Dönem:',
                        'report_btn': '📑 Rapor Al', 'risk_report_btn': '📑 Risk Raporu', 'compare_btn': '📊 Kıyasla',
                        'no_country': '--- Ülke Seçiniz ---', 'rank_h1': 'Sıra', 'rank_h2': 'Ülke', 'rank_h3': 'GSYİH', 'rank_h4': 'Kişi Başı GSYİH',
                        'gdp_pc_reel': 'Kişi Başı GSYİH (Reel)', 'gdp_pc_sagp': 'Kişi Başı GSYİH (SAGP/PPP)',
                        'gni_pc_reel': 'Kişi Başı GSMH (Reel)', 'gni_pc_sagp': 'Kişi Başı GSMH (SAGP/PPP)',
                        'risk_h1': 'Gösterge', 'risk_h2': 'Ülke 1', 'risk_h3': 'Ülke 2', 'risk_h4': 'Grup Ort.',
                        'blk_h1': 'Sıra', 'blk_h2': 'Ülke', 'blk_h3': 'Değer', 'blk_h4': 'Dünya Payı %',
                        'gdp_rank': 'GSYİH Dünya Sıralaması', 'gdp_nom': 'GSYİH (Reel, 2015 Sabit Fiyat)', 'gni_nom': 'GSMH (Reel, 2015 Sabit Fiyat)',
                        'gdp_pc': 'Kişi Başı GSYİH', 'gni_pc': 'Kişi Başı GSMH', 'sec_dist': '🏗️ Sektörel Dağılım (% GSYİH)',
                        'sec_agr': '🌾 Tarım', 'sec_ind': '🏭 Sanayi', 'sec_srv': '🏢 Hizmet',
                        'conj': '📈 Konjonktür & Makro Denge', 'grw': 'GSYİH Büyüme', 'inf': 'Enflasyon (TÜFE)',
                        'ipi': 'Sanayi Üretimi (IPI)', 'ppi': 'Üretici Fiyatları (ÜFE)',
                        'pub': '🏛️ Kamu Maliyesi ve Harcamalar', 'kamu_harc': 'Kamu Harcamaları', 'sav_harc': 'Savunma Harcamaları', 'egitim': 'Eğitim Harcamaları', 'saglik': 'Sağlık Harcamaları', 'vergi_gel': 'Vergi Gelirleri', 'butce_deng': 'Bütçe Dengesi', 'dis_borc': 'Dış Borç', 'sosyal_ref': 'Sosyal Refah',
                        'unemp': 'İşsizlik Oranı', 'cab': 'Cari İşlemler/GSYİH', 'hc': '🌱 Kalkınma ve Bölüşüm',
                        'hdi': 'İnsani Gelişmişlik', 'ihdi': 'Eşitsizliğe Uyarlanmış İGE (IHDI)', 'phdi': 'Gezegensel Baskılara Uyarlanmış İGE (PHDI)', 'gii': 'Toplumsal Cinsiyet Eşitsizliği (GII)', 'gdi': 'Toplumsal Cinsiyet Gelişimi (GDI)', 'lit': 'Okuryazarlık Oranı', 'gini': 'Gini Katsayısı', 'palma_ratio': 'Palma Oranı', 'wiid_s10s1_ratio': 'WIID (S10/S1)', 'WIID_Ratio': 'WIID Oranı (S10/S1)', 'glob_perf': '🏆 Küresel Performans',
                        'trill': 'Trilyon', 'bill': 'Milyar', 'desc_no_data': 'Bu yıl için bu göstergede yeterli veri bulunmamaktadır.',
                        'energy_source_text': '<b>KAYNAKÇA:</b> <b>Dünya Bankası WDI</b> (Enerji İthalatı Bağımlılığı) &nbsp;|&nbsp; <b>Our World in Data</b> (Kişi Başı Enerji, Karbon, Fosil, Yenilenebilir Payı)',
                        'source': 'Kaynak', 'world_share': 'Dünya Payı', 'leader': 'Lider', 'risk_map': 'Risk ve Kalkınma Haritası',
                        'benchmark': 'Kıyaslama Analizi', 'trend_sum': 'Eğilim Özeti',
                        'academic_def': 'Akademik Tanım', 'data_source': 'Veri Kaynağı',
                        'fiyat_esitsizlik': 'Fiyat & Eşitsizlik', 'ineq_chart_hdr': '◉ Eşitsizlik Karşılaştırma Grafiği',
                        'bullet_chart_title': '◉ Karşılaştırmalı Analiz Paneli', 'ineq_chart_title': 'Eşitsizlik ve İnsani Gelişmişlik Trendleri',
                        'ratio_scale': 'Rasyo Ölçeği (WIID/Palma)', 'year': 'Yıl', 'no_gini_data': 'Ülke seçiniz veya\nveri bulunamadı',
                        'price_type_lbl': 'Fiyat Türü:', 'base_year_lbl': 'Baz Yılı:',
                        'rank_narrative': "{y} yılında listelenen ilk 100 ekonomi arasında birinci sırada yer alan <span style='color:#27ae60; font-weight:bold;'>{leader}</span>, izlenen küresel ekonomik hasılanın yaklaşık <span style='font-weight:bold;'>%{share:.1f}</span>'lik dilimini kontrol etmektedir. Sıralama nominal GSYİH büyüklüğüne göre hiyerarşik olarak dizilmiştir.",
                        'blk_narrative': "{ind} göstergesi özelinde seçili yılda <span style='color:#27ae60; font-weight:bold;'>{leader}</span>, dünya toplam değerinin yaklaşık <span style='font-weight:bold;'>%{share:.1f}</span>'ini tek başına oluşturarak küresel blok liderliğini elde etmiştir.",
                        'risk_def_title': "Akademik Tanım (Kalkınma Risk Matrisi):",
                        'risk_def_text': "İki ülkenin temel makroekonomik metriklerinin görsel karşılaştırmasını sunar. Bullet chart'ta mavi çubuk = Ülke 1, kırmızı çubuk = Ülke 2, dikey siyah çizgi = Grup Ortalaması.",
                        'risk_data_reading': "Veri Okuması",
                        'risk_prod_price': "Üretim & Fiyat End.",
                        'risk_dev_gender': "Kalkınma & Cinsiyet End.",
                        'def_not_avail': "Bu gösterge için akademik tanım mevcut değil.",
                        'src_unknown': "Bilinmeyen Kaynak",
                        'blk_items': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
                        'blk_display': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
                        'ind_names': {
                            'GSYİH': 'GSYİH', 'GSMH': 'GSMH', 'Kişi Başı GSYİH': 'Kişi Başı GSYİH', 'Kişi Başı GSMH': 'Kişi Başı GSMH',
                            'Enflasyon': 'Enflasyon', 'İşsizlik': 'İşsizlik', 'Büyüme': 'Büyüme', 'Cari Denge': 'Cari Denge',
                            'Borç Oranı': 'Borç Oranı', 'Gini': 'Gini', 'Ar-Ge Yoğunluğu': 'Ar-Ge Yoğunluğu',
                            'Genç İşsizlik': 'Genç İşsizlik', 'Karbon': 'Karbon', 'Yaşam Süresi': 'Yaşam Süresi',
                            'Eğitim': 'Eğitim', 'Sağlık': 'Sağlık', 'İnsani Gelişmişlik': 'İnsani Gelişmişlik', 'Yoksulluk': 'Yoksulluk',
                            'İhracat': 'İhracat', 'İthalat': 'İthalat', 'Tarım': 'Tarım', 'Sanayi': 'Sanayi', 'Hizmetler': 'Hizmetler',
                            'Kamu Harcamaları': 'Kamu Harcamaları', 'Savunma Harcamaları': 'Savunma Harcamaları',
                            'Vergi Gelirleri': 'Vergi Gelirleri', 'Bütçe Dengesi': 'Bütçe Dengesi',
                            'Sosyal Refah': 'Sosyal Refah', 'Dış Borç': 'Dış Borç', 'İmalat': 'İmalat',
                            'Enerji-Maden': 'Enerji ve Maden Rantı', 'Demir-Çelik': 'Demir-Çelik ve Metal',
                            'Otomotiv-Makine': 'Otomotiv ve Makine', 'Lojistik': 'Lojistik ve Ulaşım',
                            'İletişim-ICT': 'Bilgi ve İletişim (ICT)', 'Finans-Sigorta': 'Finans ve Sigorta',
                            'Cari Açık': 'Cari İşlemler Dengesi', 'Dış Borç-GNI': 'Dış Borç Stoğu (% GSMH)',
                            'Risk Primi': 'Ülke Risk Primi (Proxy)', 'İthalat Karşılama': 'İthalat Karşılama (Ay)',
                            'Kısa Vadeli Borç': 'Kısa Vadeli Borç / Rezerv', 'DYY-Girişi': 'DYY Girişi (% GSYİH)',
                            'REK': 'Reel Efektif Kur (REK)', 'Reel Faiz': 'Reel Faiz Oranı',
                            'Bütçe Dengesi': 'Bütçe Dengesi (% GSYİH)', 'Borç Servisi': 'Borç Servisi / İhracat',
                            'HDI_UNDP': 'İnsani Gelişme Endeksi (HDI)', 'IHDI': 'Eşitsizliğe Uyarlanmış İGE (IHDI)',
                            'PHDI': 'Gezegensel Baskılara Uyarlanmış İGE (PHDI)', 'GII': 'Toplumsal Cinsiyet Eşitsizliği (GII)',
                            'GDI': 'Toplumsal Cinsiyet Gelişimi (GDI)', 'palma_ratio': 'Palma Oranı',
                            'WIID_Ratio': 'WIID Oranı (S10/S1)'
                        }
                    },
                    'en': {
                        'title': 'SBF Macro Data Analysis Center', 'logo': '🏛️ SBF\nMACRO TERMINAL',
                        'update_btn': '🌐 Update Data', 'nav_map': '🏠 General Map', 'nav_macro': '📊 Macroeconomics', 'nav_rank': '📊 Global Ranking',
                        'nav_ts': '📈 Time Series Anlyz.', 'nav_rd': '🌱 Development & Distribution', 'nav_pub': '🏛️ Public Finance',
                        'nav_block': '📊 Global Rankings', 'nav_bench': '🏁 Country Benchmarking', 'nav_sector': '🏗️ Sectoral Shares', 'nav_risk': '⚠️ Risk Analysis', 'nav_corr': '🔗 Correlation', 'nav_energy': '⚡ Energy Economics',
                        'theme_dark': '🌙 Dark Mode', 'theme_light': '☀️ Light Mode',
                        'search_placeholder': '🔍 Search or Select Country...', 'statik_yil': 'Static Analysis Year:',
                        'refresh_btn': 'Refresh Now', 'clear_btn': 'Clear Screen', 'copy_btn': '📋 Copy All Data',
                        'mode_instant': '📍 Instant', 'mode_period': '📅 Period',
                        'rank_title': '📊 GLOBAL ECONOMIC OUTPUT RANKING', 'yil_sec': 'Select Year:',
                        'country_lbl': 'Country:', 'country1_lbl': 'Country 1:', 'country2_lbl': 'Country 2:',
                        'ind_lbl': 'Indicator:', 'ind_sel_lbl': 'Indicator:', 'period_lbl': 'Period:',
                        'report_btn': '📑 Export Report', 'risk_report_btn': '📑 Risk Report', 'compare_btn': '📊 Compare',
                        'no_country': '--- Select Country ---', 'rank_h1': 'Rank', 'rank_h2': 'Country', 'rank_h3': 'GDP', 'rank_h4': 'GDP Per Capita',
                        'gdp_pc_reel': 'GDP Per Capita (Real)', 'gdp_pc_sagp': 'GDP Per Capita (PPP)',
                        'gni_pc_reel': 'GNI Per Capita (Real)', 'gni_pc_sagp': 'GNI Per Capita (PPP)',
                        'risk_h1': 'Indicator', 'risk_h2': 'Country 1', 'risk_h3': 'Country 2', 'risk_h4': 'Group Avg.',
                        'blk_h1': 'Rank', 'blk_h2': 'Country', 'blk_h3': 'Value', 'blk_h4': 'World Share %',
                        'gdp_rank': 'GDP Global Ranking', 'gdp_nom': 'GDP (Real, 2015 Constant)', 'gni_nom': 'GNI (Real, 2015 Constant)',
                        'gdp_pc': 'GDP Per Capita', 'gni_pc': 'GNI Per Capita', 'sec_dist': '🏗️ Sectoral Dist. (% GDP)',
                        'sec_agr': '🌾 Agriculture', 'sec_ind': '🏭 Industry', 'sec_srv': '🏢 Services',
                        'conj': '📈 Conjuncture & Macro Balance', 'grw': 'GDP Growth', 'inf': 'Inflation (CPI)',
                        'ipi': 'Industrial Production (IPI)', 'ppi': 'Producer Price Index (PPI)',
                        'pub': '🏛️ Public Finance & Expenditures', 'kamu_harc': 'Gov. Expenditure', 'sav_harc': 'Military Exp.', 'egitim': 'Education Exp.', 'saglik': 'Health Exp.', 'vergi_gel': 'Tax Revenue', 'butce_deng': 'Budget Balance', 'dis_borc': 'External Debt', 'sosyal_ref': 'Social Protection',
                        'unemp': 'Unemployment Rate', 'cab': 'Current Account/GDP', 'hc': '🌱 Development & Distribution',
                        'hdi': 'Human Development Index', 'ihdi': 'Inequality-adjusted HDI', 'phdi': 'Planetary pressures-adjusted HDI', 'gii': 'Gender Inequality Index (GII)', 'gdi': 'Gender Development Index (GDI)', 'lit': 'Literacy Rate', 'gini': 'Gini Coefficient', 'palma_ratio': 'Palma Ratio', 'wiid_s10s1_ratio': 'WIID (S10/S1)', 'WIID_Ratio': 'WIID Ratio (S10/S1)', 'glob_perf': '🏆 Global Performance',
                        'trill': 'Trillion', 'bill': 'Billion', 'desc_no_data': 'Insufficient data for this indicator in the selected year.',
                        'energy_source_text': '<b>SOURCES:</b> <b>World Bank WDI</b> (Net Energy Imports) &nbsp;|&nbsp; <b>Our World in Data</b> (Energy per Capita, Carbon, Fossil, Renewable Share)',
                        'source': 'Source', 'world_share': 'World Share', 'leader': 'Leader', 'risk_map': 'Risk and Development Map',
                        'benchmark': 'Benchmarking Analysis', 'trend_sum': 'Trend Summary',
                        'academic_def': 'Academic Definition', 'data_source': 'Data Source',
                        'fiyat_esitsizlik': 'Price & Inequality', 'ineq_chart_hdr': '◉ Inequality Comparison Chart',
                        'bullet_chart_title': '◉ Comparative Analysis Panel', 'ineq_chart_title': 'Inequality and Human Development Trends',
                        'ratio_scale': 'Ratio Scale (WIID/Palma)', 'year': 'Year', 'no_gini_data': 'Select country or\nno data found',
                        'price_type_lbl': 'Price Type:', 'base_year_lbl': 'Base Year:',
                        'rank_narrative': "In {y}, ranking first among the top 100 listed economies, <span style='color:#27ae60; font-weight:bold;'>{leader}</span> controls approximately <span style='font-weight:bold;'>{share:.1f}%</span> of the tracked global economic output. The ranking is hierarchically arranged based on nominal GDP.",
                        'blk_narrative': "For the {ind} indicator in the selected year, <span style='color:#27ae60; font-weight:bold;'>{leader}</span> achieved global block leadership by singularly accounting for approximately <span style='font-weight:bold;'>{share:.1f}%</span> of the world's total value.",
                        'risk_def_title': "Academic Definition (Development Risk Matrix):",
                        'risk_def_text': "Provides a visual comparison of key macroeconomic metrics for two countries. In the bullet chart, blue bar = Country 1, red bar = Country 2, vertical black line = Group Average.",
                        'risk_data_reading': "Data Reading",
                        'risk_prod_price': "Production & Price Ind.",
                        'risk_dev_gender': "Development & Gender Ind.",
                        'def_not_avail': "No academic definition available for this indicator.",
                        'src_unknown': "Unknown Source",
                        'blk_items': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
                        'blk_display': ['GDP', 'Growth', 'Inflation', 'Debt Ratio', 'Current Account', 'R&D Intensity'],
                        'ind_names': {
                            'GSYİH': 'GDP', 'GSMH': 'GNI', 'Kişi Başı GSYİH': 'GDP Per Capita', 'Kişi Başı GSMH': 'GNI Per Capita',
                            'Enflasyon': 'Inflation', 'İşsizlik': 'Unemployment', 'Büyüme': 'Growth', 'Cari Denge': 'Current Account',
                            'Borç Oranı': 'Debt Ratio', 'Gini': 'Gini', 'Ar-Ge Yoğunluğu': 'R&D Intensity',
                            'Genç İşsizlik': 'Youth Unemployment', 'Karbon': 'Carbon', 'Yaşam Süresi': 'Life Expectancy',
                            'Eğitim': 'Education', 'Sağlık': 'Health', 'İnsani Gelişmişlik': 'Human Development Index', 'Yoksulluk': 'Poverty',
                            'İhracat': 'Exports', 'İthalat': 'Imports', 'Tarım': 'Agriculture', 'Sanayi': 'Industry', 'Hizmetler': 'Services',
                            'Kamu Harcamaları': 'Gov Expenditure', 'Savunma Harcamaları': 'Military Exp',
                            'Vergi Gelirleri': 'Tax Revenue', 'Bütçe Dengesi': 'Budget Balance',
                            'Sosyal Refah': 'Social Protection', 'Dış Borç': 'External Debt', 'İmalat': 'Manufacturing',
                            'Enerji-Maden': 'Energy & Mining Rents', 'Demir-Çelik': 'Iron-Steel & Metal',
                            'Otomotiv-Makine': 'Automotive & Machinery', 'Lojistik': 'Logistics & Transport',
                            'İletişim-ICT': 'ICT Services', 'Finans-Sigorta': 'Finance & Insurance',
                            'Cari Açık': 'Current Account Balance', 'Dış Borç-GNI': 'External Debt (% GNI)',
                            'Risk Primi': 'Risk Premium', 'İthalat Karşılama': 'Import Cover (Months)',
                            'Kısa Vadeli Borç': 'ST Debt / Reserves', 'DYY-Girişi': 'FDI Inflows (% GDP)',
                            'REK': 'REER Index', 'Reel Faiz': 'Real Interest Rate',
                            'Bütçe Dengesi': 'Budget Balance', 'Borç Servisi': 'Debt Service / Exports',
                            'HDI_UNDP': 'Human Development Index (HDI)',
                            'IHDI': 'Inequality-adjusted HDI',
                            'PHDI': 'Planetary pressures-adjusted HDI', 'GII': 'Gender Inequality Index (GII)',
                            'GDI': 'Gender Development Index (GDI)', 'palma_ratio': 'Palma Ratio',
                            'WIID_Ratio': 'WIID Ratio (S10/S1)'
                        }
                    }
                }
                self.t = lambda k: self.langs[self.current_lang].get(k, k)
                self.apply_translations()
            
                
                
            
                main_layout.addWidget(self.sidebar); main_layout.addWidget(self.stacked_widget)
                for cb in self.findChildren(QComboBox):
                    if not isinstance(cb, CheckableComboBox): cb.setView(QListView())
                self.df = None
                self.apply_app_theme()

                for c in [self.corr_x, self.corr_y, self.corr_c, self.corr_start, self.corr_end, self.corr_year, self.chk_corr_trend, self.chk_corr_color]:
                    if hasattr(c, 'currentTextChanged'): c.currentTextChanged.connect(self.draw_corr_chart)
                    elif hasattr(c, 'stateChanged'): c.stateChanged.connect(self.draw_corr_chart)

                for c in [self.risk_c, self.risk_ind, self.risk_start, self.risk_end]:
                    c.currentTextChanged.connect(self.draw_risk_chart)

                for c in [self.sec_c, self.sec_ind, self.sec_start, self.sec_end]:
                    c.currentTextChanged.connect(self.draw_sectoral_chart)

                for c in [self.pub_c, self.pub_ind, self.pub_start, self.pub_end]:
                    c.currentTextChanged.connect(self.draw_pub_chart)

                QTimer.singleShot(100, self.load_initial_data)
            except Exception as e: log_crash(e)

    def _get_tech_profile(self, ind):
            import re
            meta_dict = self.indicator_metadata if getattr(self, 'current_lang', 'tr') == 'tr' else getattr(self, 'indicator_metadata_en', self.indicator_metadata)
            meta_raw = meta_dict.get(ind)
            if not meta_raw: return ""
        
            is_en = getattr(self, 'current_lang', 'tr') == 'en'

            if isinstance(meta_raw, dict):
                olcum = meta_raw.get('birim', '')
                metod = meta_raw.get('metodoloji', '')
                code_disp = meta_raw.get('kod', '')
                if is_en:
                    tech_title = 'Technical Profile'
                    lbl_basis = 'Measurement Unit'
                    lbl_method = 'Methodology'
                    lbl_code = 'Source Code'
                else:
                    tech_title = 'Teknik Künye'
                    lbl_basis = 'Ölçüm Birimi'
                    lbl_method = 'Metodoloji'
                    lbl_code = 'Kaynak Kodu'
            
                return f"""
                <div style="margin-top:10px; padding:10px; background-color:#fef9e7; border-left:4px solid #f1c40f; border-radius:4px;">
                    <b style="color:#d35400; font-size:13px;">{tech_title}</b>
                    <table style="margin-top:5px; width:100%; color:#2c3e50; font-size:12px; border-collapse:collapse;">
                        <tr><td style="width:120px; padding:2px 0;"><b>{lbl_basis}:</b></td><td>{olcum}</td></tr>
                        <tr><td style="padding:2px 0;"><b>{lbl_method}:</b></td><td>{metod}</td></tr>
                        <tr><td style="padding:2px 0;"><b>{lbl_code}:</b></td><td><code style="background:#fad7a1; padding:2px 4px; border-radius:3px; color:#d35400;">{code_disp}</code></td></tr>
                    </table>
                </div>
                """

            source_raw = meta_raw[2]

            code_match = re.search(r'\((.*?)\)', source_raw)
            code = code_match.group(1) if code_match else ""

            # ── Ölçüm Esası (Measurement Basis) — akademik standard
            if '.ZS' in code:
                if 'GB.XPD.RSDV' in code:
                    olcum = ('R&D Intensity — Share in GDP (%)' if is_en
                             else 'Ar-Ge Yoğunluğu — GSYİH\'ye Oran (%)')
                else:
                    olcum = ('Share in GDP / Total (%)' if is_en
                             else 'GSYİH veya Toplam İçindeki Pay (%)')
            elif '.ZG' in code:
                olcum = ('Annual Rate of Change (%)' if is_en
                         else 'Yıllık Değişim Oranı (%)')
            elif '.CD' in code:
                if 'PCAP' in code:
                    olcum = ('Current US Dollars — Per Capita (Nominal)' if is_en
                             else 'Cari ABD Doları — Kişi Başına (Nominal)')
                else:
                    olcum = ('Current US Dollars — Aggregate (Nominal)' if is_en
                             else 'Cari ABD Doları — Toplam (Nominal)')
            elif '.KD' in code:
                if 'PCAP' in code:
                    olcum = ('Constant US Dollars 2015 — Per Capita (Real)' if is_en
                             else 'Sabit ABD Doları 2015 — Kişi Başına (Reel)')
                else:
                    olcum = ('Constant US Dollars 2015 — Aggregate (Real)' if is_en
                             else 'Sabit ABD Doları 2015 — Toplam (Reel)')
            elif '.PC' in code:
                olcum = ('Metric Tons per Capita' if is_en else 'Metrik Ton / Kişi Başına')
            elif ind in ('HDI_UNDP', 'IHDI', 'PHDI', 'GII', 'GDI'):
                olcum = ('Index Score (0–1 scale)' if is_en else 'Endeks Puanı (0–1 ölçeği)')
            elif ind == 'Gini':
                olcum = ('Index Score (0–100 scale)' if is_en else 'Endeks Puanı (0–100 ölçeği)')
            elif ind in ('palma_ratio', 'WIID_Ratio'):
                olcum = ('Ratio (dimensionless)' if is_en else 'Oran (Birimsiz)')
            else:
                olcum = ('Index / Ratio' if is_en else 'İndeks / Oran')

            # ── Metodoloji
            if '.CD' in code:
                metod = ('Current Prices — Nominal Valuation' if is_en
                         else 'Cari Fiyatlar — Nominal Değerleme')
            elif '.KD' in code:
                metod = ('Constant Prices — Real Valuation (Base Year 2015)' if is_en
                         else 'Sabit Fiyatlar — Reel Değerleme (Baz Yılı 2015)')
            elif '.ZS' in code:
                metod = ('Percentage of GDP or aggregate total' if is_en
                         else 'GSYİH veya toplam içindeki yüzde pay')
            elif '.ZG' in code:
                metod = ('Annual percentage change (year-on-year)' if is_en
                         else 'Yıllık yüzde değişim (yıldan yıla)')
            elif 'PP' in code:
                metod = ('Purchasing Power Parity (PPP) Adjusted' if is_en
                         else 'Satın Alma GüCü Paritesi (SGP) Düzeltmeli')
            else:
                metod = ('Composite / Statistical Calculation' if is_en
                         else 'Bileşik / İstatistiksel Hesaplama')

            if is_en:
                tech_title = 'Technical Profile'
                lbl_basis = 'Measurement Basis'
                lbl_method = 'Methodology'
                lbl_code = 'Source Code'
            else:
                tech_title = 'Teknik Künye'
                lbl_basis = 'Ölçüm Esası'
                lbl_method = 'Metodoloji'
                lbl_code = 'Kaynak Kodu'

            code_disp = code if code else ('Unknown' if is_en else 'Bilinmiyor')

            return f"""
            <div style="margin-top:10px; padding:10px; background-color:#fef9e7; border-left:4px solid #f1c40f; border-radius:4px;">
                <b style="color:#d35400; font-size:13px;">{tech_title}</b>
                <table style="margin-top:5px; width:100%; color:#2c3e50; font-size:12px; border-collapse:collapse;">
                    <tr><td style="width:120px; padding:2px 0;"><b>{lbl_basis}:</b></td><td>{olcum}</td></tr>
                    <tr><td style="padding:2px 0;"><b>{lbl_method}:</b></td><td>{metod}</td></tr>
                    <tr><td style="padding:2px 0;"><b>{lbl_code}:</b></td><td><code style="background:#fad7a1; padding:2px 4px; border-radius:3px; color:#d35400;">{code_disp}</code></td></tr>
                </table>
            </div>
            """

    def _get_unit_label(self, ind):
            """Returns a human-readable unit string for a given indicator column name."""
            import re
            meta_dict = self.indicator_metadata if getattr(self, 'current_lang', 'tr') == 'tr' else getattr(self, 'indicator_metadata_en', self.indicator_metadata)
            meta_raw = meta_dict.get(ind)
            if isinstance(meta_raw, dict):
                return meta_raw.get('birim', '')
        
            code = ""
            if meta_raw:
                m = re.search(r'\((.*?)\)', meta_raw[2])
                if m: code = m.group(1)
            is_en = getattr(self, 'current_lang', 'tr') == 'en'
            if '.ZS' in code:
                return '% of GDP' if is_en else '% GSYİH'
            elif '.ZG' in code:
                return '% (Annual)' if is_en else '% (Yıllık)'
            elif '.CD' in code:
                return ('USD' if 'PCAP' in code else 'Billion USD') if is_en else ('$ (ABD Doları)' if 'PCAP' in code else 'Milyar $')
            elif '.KD' in code:
                return ('USD (Real)' if 'PCAP' in code else 'Billion USD (Real)') if is_en else ('$ Reel' if 'PCAP' in code else 'Milyar $ (Reel)')
            elif '.PC' in code:
                return 'Metric Tons / Capita' if is_en else 'Metrik Ton / Kişi'
            elif ind in ('HDI_UNDP', 'IHDI', 'PHDI', 'GII', 'GDI'):
                return 'Index (0–1)' if is_en else 'İndeks (0–1)'
            elif ind == 'Gini':
                return 'Gini (0–100)'
            elif ind in ('palma_ratio', 'WIID_Ratio'):
                return 'Ratio' if is_en else 'Oran'
            elif ind in ('Yaşam Süresi',):
                return 'Years' if is_en else 'Yıl'
            return ''

    def _get_formatted_source(self, ind, iso=None):
            import re
            meta_dict = self.indicator_metadata if getattr(self, 'current_lang', 'tr') == 'tr' else getattr(self, 'indicator_metadata_en', self.indicator_metadata)
            meta_raw = meta_dict.get(ind)
            if not meta_raw:
                return ""
            
            is_en = getattr(self, 'current_lang', 'tr') == 'en'
        
            src_text = "World Bank WDI" if is_en else "D\u00fcnya Bankas\u0131 WDI"
            code = ""
            scale = ""
        
            if isinstance(meta_raw, dict):
                code = meta_raw.get('kod', '')
                source_raw = meta_raw.get('metodoloji', '')
                if not code and source_raw:
                    code_match = re.search(r'\((.*?)\)', source_raw)
                    if code_match:
                        code = code_match.group(1)
                
                check_str = code + " " + source_raw
                if "UNDP" in check_str or "hdr.undp" in check_str:
                    src_text = "UNDP"
                elif "WIID" in check_str or "SWIID" in check_str:
                    src_text = "SWIID / WIID"
                elif "Mkt" in check_str or "Market" in check_str:
                    src_text = "Market Data"
                elif "Our World in Data" in check_str:
                    src_text = "Our World in Data"
                elif "V-Dem" in check_str:
                    src_text = "V-Dem Institute"
                elif "World Bank" in check_str:
                    src_text = "World Bank WDI" if is_en else "Dünya Bankası WDI"
                elif source_raw:
                    src_text = source_raw.split('(')[0].strip()
            else:
                source_raw = meta_raw[2] if len(meta_raw) > 2 else ""
                code_match = re.search(r'\\((.*?)\\)', source_raw)
                code = code_match.group(1) if code_match else source_raw
                if "World Bank" in source_raw:
                    src_text = "World Bank WDI" if is_en else "D\u00fcnya Bankas\u0131 WDI"
                elif "UNDP" in source_raw:
                    src_text = "UNDP"
                elif "V-Dem" in source_raw:
                    src_text = "V-Dem Institute"
                elif "ASPIRE" in source_raw:
                    src_text = "World Bank ASPIRE" if is_en else "D\u00fcnya Bankas\u0131 ASPIRE"
                else:
                    src_text = source_raw.split('(')[0].strip()

            if '.ZS' in code:
                scale = '% of GDP' if is_en else '% GSY\u0130H'
            elif '.ZG' in code:
                scale = 'Annual % Change' if is_en else 'Y\u0131ll\u0131k % De\u011fi\u015fim'
            elif '.CD' in code:
                scale = 'Current USD' if is_en else 'Cari ABD Dolar\u0131'
            elif '.KD' in code:
                scale = 'Constant 2015 USD' if is_en else 'Sabit 2015 ABD Dolar\u0131'
            elif '.PC' in code:
                scale = 'Metric Tons / Capita' if is_en else 'Metrik Ton / Ki\u015fi Ba\u015f\u0131na'
            elif ind in ('HDI_UNDP', 'IHDI', 'PHDI', 'GII', 'GDI'):
                scale = 'Index (0-1)' if is_en else 'Endeks (0-1)'
            elif ind == 'Gini':
                scale = 'Index (0-100)' if is_en else 'Endeks (0-100)'
            elif ind in ('palma_ratio', 'WIID_Ratio'):
                scale = 'Ratio' if is_en else 'Oran'
            elif ind in ('Ya\u015fam S\u00fcresi',):
                scale = 'Years' if is_en else 'Y\u0131l'
            else:
                scale = 'Index / Value' if is_en else 'Endeks / De\u011fer'

            # Tayvan ve Kuzey Kore i\u00e7in kaynak override
            if iso == 'TWN':
                src_text = "CIA World Factbook"
                code = "factbook/factbook.json (east-n-southeast-asia/tw.json)"
                scale = "2021-2024 Tahmini" if not is_en else "2021-2024 Estimates"
            elif iso == 'PRK':
                src_text = "CIA World Factbook + Bank of Korea" if not is_en else "CIA World Factbook + Bank of Korea"
                code = "factbook/factbook.json (kn.json) + BoK GDP Estimates"
                scale = "2021-2024 CIA, 1990-2020 BoK" if not is_en else "2021-2024 CIA, 1990-2020 BoK"
            
            lbl_src = "SOURCE" if is_en else "KAYNAK"
            lbl_ind = "INDICATOR" if is_en else "G\u00d6STERGE"
            lbl_scl = "SCALE" if is_en else "\u00d6L\u00c7\u00dcT"
        
            return f"<span style='font-family: monospace; font-size: 12px; color: #2c3e50; background-color: #f0f3f4; padding: 3px 6px; border-radius: 4px; border: 1px solid #d5dbdb;'>{lbl_src}: {src_text} &nbsp;|&nbsp; {lbl_ind}: {code} &nbsp;|&nbsp; {lbl_scl}: {scale}</span>"

    def _get_metadata(self, ind, iso=None):
            meta_dict = self.indicator_metadata if self.current_lang == 'tr' else getattr(self, 'indicator_metadata_en', self.indicator_metadata)
            meta = meta_dict.get(ind)
            if meta:
                formatted_source = self._get_formatted_source(ind, iso=iso)
                if isinstance(meta, dict):
                    ind_en_name = self.langs[self.current_lang].get('ind_names', {}).get(ind, ind)
                    name = ind_en_name if self.current_lang == 'en' else ind
                    return (name, meta.get('tanim', ''), formatted_source)
                
                def_txt = meta[1]
                source_txt = formatted_source
            
                orig_src = meta[2] if len(meta) > 2 else ""
                if "NY.GDP.MKTP.CD" in orig_src or "NY.GNP.MKTP.CD" in orig_src:
                    nom_info = " (Nominal - Cari ABD Dolar\u0131)" if self.current_lang == 'tr' else " (Nominal - Current US$)"
                    def_txt += f" <span style='color:#c0392b; font-weight:bold;'>{nom_info}</span>"
                elif ".KD" in orig_src:
                    reel_info = " (Reel - Sabit Fiyatlar - Baz Y\u0131l\u0131)" if self.current_lang == 'tr' else " (Real - Constant Prices - Base Year)"
                    def_txt += f" <span style='color:#2980b9; font-weight:bold;'>{reel_info}</span>"
                
                return (meta[0], def_txt, source_txt)
            ind_en_name = self.langs[self.current_lang].get('ind_names', {}).get(ind, ind)
            return (ind_en_name, self.t('def_not_avail'), self.t('src_unknown'))

    def load_initial_data(self):
            if os.path.exists(parquet_path):
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.load_worker = ParquetLoadWorker(parquet_path)
                self.load_worker.finished.connect(self.on_data_loaded)
                self.load_worker.error.connect(lambda e: self._handle_worker_error("Veri Yükleme", e))
                self.load_worker.start()
            else: QMessageBox.information(self, "Veri Eksik", "Lütfen 'Verileri Güncelle' butonuna basın.")

    def on_data_loaded(self, df):
            renames = {
                'Kişi_Başı_Gelir': 'Kişi Başı GSYİH',
                'Kişi Başı Gelir': 'Kişi Başı GSYİH',
                'GNI_PC': 'Kişi Başı GSMH',
                'Cari_Denge': 'Cari Denge',
                'Borç_Oranı': 'Borç Oranı',
                'Genç_İşsizlik': 'Genç İşsizlik',
                'Yaşam_Süresi': 'Yaşam Süresi',
                'ArGe_Harcaması': 'Ar-Ge Yoğunluğu',
                'Ar-Ge Harcaması': 'Ar-Ge Yoğunluğu',
                'wiid_s10s1_ratio': 'WIID_Ratio'
            }
            self.df = df.rename(columns=renames)
            # ── Parquet'ten gelen duplicate kolonları hemen temizle ──
            self.df = self.df.loc[:, ~self.df.columns.duplicated(keep='first')]
        
            if 'Top10' in self.df.columns and 'Bottom10' in self.df.columns:
                if 'WIID_Ratio' not in self.df.columns:
                    self.df['WIID_Ratio'] = (pd.to_numeric(self.df['Top10'], errors='coerce') / 
                                             pd.to_numeric(self.df['Bottom10'], errors='coerce').replace(0, np.nan))
            if 'Top10' in self.df.columns and 'Low20' in self.df.columns and 'Sec20' in self.df.columns:
                if 'palma_ratio' not in self.df.columns:
                    self.df['palma_ratio'] = (pd.to_numeric(self.df['Top10'], errors='coerce') / 
                                              (pd.to_numeric(self.df['Low20'], errors='coerce') + 
                                               pd.to_numeric(self.df['Sec20'], errors='coerce')).replace(0, np.nan))

            # ── Kişi Başı Reel türetme — kolon yoksa oluştur, varsa NaN hücreleri doldur ──
            # Formül: Kişi Başı GSYİH (Reel) = GSYİH(Reel) × Kişi Başı GSYİH / GSYİH
            _has = lambda c: c in self.df.columns
            if _has('GSYİH (Reel)') and _has('Kişi Başı GSYİH') and _has('GSYİH'):
                gdp_n = pd.to_numeric(self.df['GSYİH'], errors='coerce').replace(0, np.nan)
                gdp_derived = (pd.to_numeric(self.df['GSYİH (Reel)'], errors='coerce') *
                               pd.to_numeric(self.df['Kişi Başı GSYİH'], errors='coerce') / gdp_n)
                if 'Kişi Başı GSYİH (Reel)' not in self.df.columns:
                    self.df['Kişi Başı GSYİH (Reel)'] = gdp_derived
                else:
                    mask = self.df['Kişi Başı GSYİH (Reel)'].isna()
                    self.df.loc[mask, 'Kişi Başı GSYİH (Reel)'] = gdp_derived[mask]

            if _has('GSMH (Reel)') and _has('Kişi Başı GSMH') and _has('GSMH'):
                gni_n = pd.to_numeric(self.df['GSMH'], errors='coerce').replace(0, np.nan)
                gni_derived = (pd.to_numeric(self.df['GSMH (Reel)'], errors='coerce') *
                               pd.to_numeric(self.df['Kişi Başı GSMH'], errors='coerce') / gni_n)
                if 'Kişi Başı GSMH (Reel)' not in self.df.columns:
                    self.df['Kişi Başı GSMH (Reel)'] = gni_derived
                else:
                    mask = self.df['Kişi Başı GSMH (Reel)'].isna()
                    self.df.loc[mask, 'Kişi Başı GSMH (Reel)'] = gni_derived[mask]
            # ────────────────────────────────────────────────────────────────────

            # ── Yerel Sosyal Göstergeler ile Birleştir (UNDP HDI + V-Dem) ──
            self.df = merge_social_indicators(self.df)
        
            QApplication.restoreOverrideCursor()
            self.ui_refresh()
            self.update_map()
            self.plot_macro()
            self._start_imf_fetch()

    def _handle_worker_error(self, ctx, err):
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Hata", f"{ctx} sırasında hata: {err}")

    def clear_timeout_blacklist(self):
            import os, json
            from sbf_terminal.constants import blacklist_path
            if not os.path.exists(blacklist_path):
                QMessageBox.information(self, "Kara Liste", "Kara liste zaten boş, silinecek bir kayıt yok.")
                return
            try:
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    bl = json.load(f)
                count = len(bl)
                os.remove(blacklist_path)
                QMessageBox.information(self, "Kara Liste Temizlendi",
                    f"✅ {count} gösterge kara listeden kaldırıldı.\n\n"
                    "Bir sonraki 'Verileri Güncelle' işleminde hepsi tekrar denenecek.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Kara liste silinemedi: {e}")

    def start_data_update(self):
            self.update_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
        
            # --- Akıllı Tarama: Yeni Göstergeleri Tespit Et ---
            # Önemli: self.df değil, PARQUET kolonları esas alınır.
            # (on_data_loaded'da bellekte türetilen kolonlar parquet'te yok — yanlış 'mevcut' tespiti önlenir)
            parquet_cols = set()
            if os.path.exists(parquet_path):
                try:
                    import pyarrow.parquet as pq
                    parquet_cols = set(pq.read_schema(parquet_path).names)
                except Exception:
                    parquet_cols = set(self.df.columns) if (hasattr(self, 'df') and self.df is not None) else set()
            existing_cols = parquet_cols if parquet_cols else (
                set(self.df.columns) if (hasattr(self, 'df') and self.df is not None) else set()
            )
        
            new_keys = []
        
            if not existing_cols or 'GSYİH' not in existing_cols:
                # Veri yok → sıfırdan 25 yıl
                target_years = list(range(2000, 2026))
                print("[SmartScanner] ✅ İlk kurulum — tüm 25 yıl çekilecek.")
            else:
                target_years = list(range(2023, 2026))  # Mevcut göstergeler için son 3 yıl
                # INDICATORS sözlüğünden parquet'te olmayan kolon adlarını bul → bu WB kodları 25 yıl indirilecek
                for wb_code, col_name in DataWorker.INDICATORS.items():
                    if col_name not in existing_cols:
                        new_keys.append(wb_code)
                if new_keys:
                    new_names = [DataWorker.INDICATORS[k] for k in new_keys]
                    print(f"[SmartScanner] 🔍 Yeni göstergeler tespit edildi (25 yıl indirilecek): {new_names}")
                print(f"[SmartScanner] Mevcut göstergeler için hedef yıllar: {target_years}")

            self.worker = DataWorker(years=target_years, new_keys=new_keys)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.on_update_finished)
            self.worker.error.connect(lambda x: QMessageBox.critical(self, "Hata", x))
            self.worker.start()

    def on_update_finished(self, fdf):
            try:
                if fdf is None or fdf.empty:
                    raise ValueError("Veri seti boş döndü.")

                if 'GSYİH' in fdf.columns:
                    fdf['GSYİH'] = pd.to_numeric(fdf['GSYİH'], errors='coerce')
                    fdf['GSYİH_Sıra'] = fdf.groupby('Yıl')['GSYİH'].rank(ascending=False, method='min')
                else:
                    print("⚠️ Uyarı: GSYİH verisi bulunamadı, sıralama yapılamadı.")
                
                # Inequality Ratios (Palma & WIID)
                if 'Top10' in fdf.columns and 'Bottom10' in fdf.columns:
                    fdf['WIID_Ratio'] = (pd.to_numeric(fdf['Top10'], errors='coerce') / 
                                         pd.to_numeric(fdf['Bottom10'], errors='coerce').replace(0, np.nan))
                if 'Top10' in fdf.columns and 'Low20' in fdf.columns and 'Sec20' in fdf.columns:
                    fdf['palma_ratio'] = (pd.to_numeric(fdf['Top10'], errors='coerce') / 
                                          (pd.to_numeric(fdf['Low20'], errors='coerce') + 
                                           pd.to_numeric(fdf['Sec20'], errors='coerce')).replace(0, np.nan))
                # ── Akıllı Güncelleme Motoru (WB Data Upsert) ──
                # NOT: social_indicators.csv (HDI/V-Dem verisi) hiçbir zaman değiştirilmez/silinmez.
                # Bu dosya yalnızca OKUNUR — yazma veya silme işlemi kesinlikle yapılmaz.
                sde = SmartDataEngine(parquet_path, social_csv_path)
                sde.load()
            
                if sde.df is None or sde.df.empty:
                    sde._df = fdf
                    sde._mark_manual_sources()
                else:
                    sde.upsert_api(fdf, SmartDataEngine.WB_TAG)
                
                self.df = sde.df
                # ── Duplicate kolon koruması ──
                self.df = self.df.loc[:, ~self.df.columns.duplicated(keep='first')]
            
                # ── Yerel Sosyal Göstergeler ile Birleştir (UNDP HDI + V-Dem) ──
                self.df = merge_social_indicators(self.df)
                self.df = self.df.loc[:, ~self.df.columns.duplicated(keep='first')]
            
                # ── Türetme: API'de eksik kalan per-capita reel değerleri formidülle doldur ──
                _h = lambda c: c in self.df.columns
                if _h('GSYİH (Reel)') and _h('Kişi Başı GSYİH') and _h('GSYİH'):
                    gdp_n = pd.to_numeric(self.df['GSYİH'], errors='coerce').replace(0, np.nan)
                    derived = (pd.to_numeric(self.df['GSYİH (Reel)'], errors='coerce') *
                               pd.to_numeric(self.df['Kişi Başı GSYİH'], errors='coerce') / gdp_n)
                    if 'Kişi Başı GSYİH (Reel)' not in self.df.columns:
                        self.df['Kişi Başı GSYİH (Reel)'] = derived
                    else:
                        mask = self.df['Kişi Başı GSYİH (Reel)'].isna()
                        self.df.loc[mask, 'Kişi Başı GSYİH (Reel)'] = derived[mask]
                if _h('GSMH (Reel)') and _h('Kişi Başı GSMH') and _h('GSMH'):
                    gni_n = pd.to_numeric(self.df['GSMH'], errors='coerce').replace(0, np.nan)
                    derived = (pd.to_numeric(self.df['GSMH (Reel)'], errors='coerce') *
                               pd.to_numeric(self.df['Kişi Başı GSMH'], errors='coerce') / gni_n)
                    if 'Kişi Başı GSMH (Reel)' not in self.df.columns:
                        self.df['Kişi Başı GSMH (Reel)'] = derived
                    else:
                        mask = self.df['Kişi Başı GSMH (Reel)'].isna()
                        self.df.loc[mask, 'Kişi Başı GSMH (Reel)'] = derived[mask]
                # ────────────────────────────────────────────────────────
            
                sde._df = self.df

                # ── Tayvan & Kuzey Kore (IMF / BoK) ──
                try:
                    from extra_data import get_extra_countries_data
                    extra_df = get_extra_countries_data()
                    if extra_df is not None and not extra_df.empty:
                        # Mevcut verilerden TWN/PRK satırlarını çıkar (tekrar eklemeye karşı)
                        self.df = self.df[~self.df['ISO'].isin(['TWN', 'PRK'])]
                        self.df = pd.concat([self.df, extra_df], ignore_index=True)
                        sde._df = self.df
                        print(f"[ExtraData] Tayvan+K.Kore eklendi: {len(extra_df)} satır")
                except Exception as ex:
                    print(f"[ExtraData] Eklenemedi: {ex}")

                # ── Akıllı Güncelleme Motoru: yedekle + kaydet ──
                if 'GSYİH' in self.df.columns or 'Gini' in self.df.columns:
                    sde.backup_and_save()
                self.update_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
                QMessageBox.information(self, "Başarılı", "Genişletilmiş veri seti (2010-2025) kullanıma hazır!")
                self.ui_refresh()
                # Tüm grafikleri yenile — veri çekiminden sonra hiçbir tab boş kalmasın
                for fn in [self.plot_macro, self.draw_sectoral_chart, self.draw_risk_chart,
                           self.draw_pub_chart, self.draw_inequality_chart, self.draw_welfare_chart,
                           self.plot_blocks, self.update_map]:
                    try: fn()
                    except Exception: pass
                self._start_imf_fetch()
            except Exception as e:
                import traceback; traceback.print_exc()
                self.update_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Hata", f"Veri işlenirken hata oluştu: {str(e)}")

    def _start_imf_fetch(self):
            """IMFWorker'ı arka planda başlatır."""
            try:
                self.imf_worker = IMFWorker()
                self.imf_worker.finished.connect(self.on_imf_data_ready)
                self.imf_worker.error.connect(lambda e: print(f"[IMF] Worker hatası: {e}"))
                self.imf_worker.start()
                print("[IMF] Veri çekimi başlatıldı (IPI, PPI)...")
            except Exception as e:
                print(f"[IMF] Başlatma hatası: {e}")

    def on_imf_data_ready(self, imf_df):
            """IMF verisi hazır — SmartDataEngine ile korumalı upsert."""
            if imf_df is None or imf_df.empty or self.df is None:
                print("[IMF] Veri boş, birleştirme atlandı.")
                return
            try:
                imf_df = imf_df[imf_df['Yıl'].between(2000, 2025)].copy()
                # SmartDataEngine üzerinden korumalı upsert
                sde = SmartDataEngine(parquet_path, social_csv_path)
                sde._df  = self.df        # Mevcut df'i kullan
                sde._src = None           # Kaynak matrisi yoksa koruma UN sütunlarıyla sınırlı kalacak
                sde._mark_manual_sources()
                sde.upsert_api(imf_df, SmartDataEngine.IMF_TAG)
                self.df = sde.df
                imf_cols = [c for c in ['IPI', 'PPI'] if c in imf_df.columns]
                print(f"[IMF] Entegre edildi: {imf_cols}")
                self.ui_refresh()
            except Exception as e:
                print(f"[IMF] Birleştirme hatası: {e}")

    def _display_country(self, en_name):
            """İngilizce ülke adını mevcut dile göre döndür."""
            if getattr(self, 'current_lang', 'tr') == 'tr':
                return COUNTRY_TR.get(en_name, en_name)
            return en_name

    def _en_country(self, display_name):
            """Görünüm adından İngilizce (iç) ülke adına dönüştürür."""
            if getattr(self, 'current_lang', 'tr') == 'tr':
                return COUNTRY_TR_REV.get(display_name, display_name)
            return display_name

    def _sort_key(self, s):
            """Türkçe kurallarına uygun sıralama anahtarı döndürür."""
            return s.replace('I','ı').replace('İ','i').lower()\
                .replace('ç','c~').replace('ğ','g~').replace('ı','h~').replace('ö','o~').replace('ş','s~').replace('ü','u~')

    def switch_page(self, page_idx):
            self.stacked_widget.setCurrentIndex(page_idx)
            for b in self.nav_btns:
                b.setStyleSheet(self.get_nav_style(getattr(b, 'target_idx', -1) == page_idx))

    def on_map_ready(self, html):
            self.wv.setHtml(html)
            QApplication.restoreOverrideCursor()

    def on_map_error(self, e):
            import traceback; traceback.print_exc()
            self.wv.setHtml(f"<h3>Harita Yüklenemedi</h3><p>{str(e)}</p>")
            QApplication.restoreOverrideCursor()

    def ui_refresh(self):
            if self.df is None: return
            years = [str(y) for y in sorted(self.df['Yıl'].unique().tolist())]
        
            # Populate country/indicator combos (sadece bir kez)
            if not getattr(self, '_country_en_list', None):
                en_names = self.df['Ülke'].unique().tolist()
                self._country_en_list = en_names
                sorted_names = sorted([self._display_country(n) for n in en_names], key=self._sort_key)
                clist = [self.t('no_country')] + sorted_names
                inds = [c for c in self.df.columns if c not in ['ISO','Yıl','Ülke','Lon','Lat','Gelir_Grubu','aggregate','region','incomeLevel','name', 'GSYİH_Sıra', 'v', 'Series', 'Val', 'Top10', 'Bottom10', 'GSYİH (Reel)', 'GSMH (Reel)', 'Sec20', 'Low20', 'Okuryazarlık']]
                ind_names = self.langs[self.current_lang].get('ind_names', {})
                inds_display = [ind_names.get(c, c.replace('_', ' ')) for c in inds]
            
                sorted_inds = sorted(zip(inds, inds_display), key=lambda x: self._sort_key(x[1]))
                self._ind_keys = [x[0] for x in sorted_inds]
                self._ind_display = [x[1] for x in sorted_inds]
            
                for cmb in [self.blk_cmb, self.corr_x, self.corr_y]:
                    cmb.blockSignals(True); cmb.clear(); cmb.addItems(self._ind_display); cmb.blockSignals(False)
                if not self.blk_cmb.currentText() and len(self._ind_display) > 0: self.blk_cmb.setCurrentIndex(0)
                if not self.corr_x.currentText() and len(self._ind_display) > 0: self.corr_x.setCurrentIndex(0)
                if not self.corr_y.currentText() and len(self._ind_display) > 1: self.corr_y.setCurrentIndex(1)
            
                for cmb in [self.rd_country1, self.rd_country2, self.search_combo, self.pub_c, self.sec_c, self.risk_c, getattr(self, 'energy_country', None)]:
                    if cmb is None: continue
                    cmb.blockSignals(True); cmb.clear(); cmb.addItems(clist); cmb.blockSignals(False)
            
                # Korelasyon için özel "Hepsi" seçeneği
                all_lbl = "🌍 Hepsi (Tüm Ülkeler)" if self.current_lang == 'tr' else "🌍 All (All Countries)"
                clist_corr = [all_lbl] + clist[1:]
                self.corr_c.blockSignals(True); self.corr_c.clear(); self.corr_c.addItems(clist_corr); self.corr_c.blockSignals(False)
            
                self.search_combo.setCurrentIndex(0)
                cm = QCompleter(clist); cm.setCaseSensitivity(Qt.CaseInsensitive); self.search_combo.setCompleter(cm)
        
            # Yıl comboboxları her zaman yeniden doldurulur (yeni veri çekildiğinde güncellenmesi için)


            if hasattr(self, 'macro_start'):
                prev_m_s, prev_m_e = self.macro_start.currentText(), self.macro_end.currentText()
                self.macro_start.blockSignals(True); self.macro_start.clear(); self.macro_start.addItems(years)
                self.macro_start.setCurrentText(prev_m_s) if prev_m_s in years else self.macro_start.setCurrentIndex(0)
                self.macro_start.blockSignals(False)
            
                self.macro_end.blockSignals(True); self.macro_end.clear(); self.macro_end.addItems(years)
                self.macro_end.setCurrentText(prev_m_e) if prev_m_e in years else self.macro_end.setCurrentIndex(len(years)-1)
                self.macro_end.blockSignals(False)
            
            if hasattr(self, 'sec_start'):
                prev_s_s, prev_s_e = self.sec_start.currentText(), self.sec_end.currentText()
                self.sec_start.blockSignals(True); self.sec_start.clear(); self.sec_start.addItems(years)
                self.sec_start.setCurrentText(prev_s_s) if prev_s_s in years else self.sec_start.setCurrentIndex(0)
                self.sec_start.blockSignals(False)
            
                self.sec_end.blockSignals(True); self.sec_end.clear(); self.sec_end.addItems(years)
                self.sec_end.setCurrentText(prev_s_e) if prev_s_e in years else self.sec_end.setCurrentIndex(len(years)-1)
                self.sec_end.blockSignals(False)
            
            if hasattr(self, 'macro_c'):
                prev_m_c = self.macro_c.currentText()
                if self.macro_c.count() > 0:
                    existing = [self.macro_c.itemText(k) for k in range(self.macro_c.count())]
                    # Yıl değişimi: ülke comboları zaten dolu, mevcut itemlerden oluştur
                    clist_macro = ["🌍 World (Global Analysis)" if self.current_lang == 'en' else "🌍 Dünya (Küresel Analiz)"] + existing[1:]
                else:
                    # İlk yükleme: yukarıdaki if-bloğu çalıştı, clist tanımlıdır
                    clist_macro = ["🌍 World (Global Analysis)" if self.current_lang == 'en' else "🌍 Dünya (Küresel Analiz)"] + clist[1:]
                self.macro_c.blockSignals(True); self.macro_c.clear(); self.macro_c.addItems(clist_macro)
                if prev_m_c in clist_macro: self.macro_c.setCurrentText(prev_m_c)
                self.macro_c.blockSignals(False)


            prev_pub_start = self.pub_start.currentText()
            prev_pub_end = self.pub_end.currentText()
        
            self.pub_start.blockSignals(True); self.pub_start.clear(); self.pub_start.addItems(years)
            self.pub_start.setCurrentText(prev_pub_start) if prev_pub_start in years else self.pub_start.setCurrentIndex(0)
            self.pub_start.blockSignals(False)
        
            self.pub_end.blockSignals(True); self.pub_end.clear(); self.pub_end.addItems(years)
            self.pub_end.setCurrentText(prev_pub_end) if prev_pub_end in years else self.pub_end.setCurrentIndex(len(years)-1)
            self.pub_end.blockSignals(False)

            if hasattr(self, 'risk_start'):
                prev_r_s, prev_r_e = self.risk_start.currentText(), self.risk_end.currentText()
                self.risk_start.blockSignals(True); self.risk_start.clear(); self.risk_start.addItems(years)
                self.risk_start.setCurrentText(prev_r_s) if prev_r_s in years else self.risk_start.setCurrentIndex(0)
                self.risk_start.blockSignals(False)
                self.risk_end.setCurrentText(prev_r_e) if prev_r_e in years else self.risk_end.setCurrentIndex(len(years)-1)
                self.risk_end.blockSignals(False)

            if hasattr(self, 'corr_start'):
                prev_c_s, prev_c_e = self.corr_start.currentText(), self.corr_end.currentText()
                self.corr_start.blockSignals(True); self.corr_start.clear(); self.corr_start.addItems(years)
                self.corr_start.setCurrentText(prev_c_s) if prev_c_s in years else self.corr_start.setCurrentIndex(0)
                self.corr_start.blockSignals(False)
                self.corr_end.blockSignals(True); self.corr_end.clear(); self.corr_end.addItems(years)
                self.corr_end.setCurrentText(prev_c_e) if prev_c_e in years else self.corr_end.setCurrentIndex(len(years)-1)
                self.corr_end.blockSignals(False)
            
            if hasattr(self, 'corr_year'):
                prev_c_y = self.corr_year.currentText()
                self.corr_year.blockSignals(True); self.corr_year.clear(); self.corr_year.addItems(years)
                self.corr_year.setCurrentText(prev_c_y) if prev_c_y in years else (self.corr_year.setCurrentText('2024') if '2024' in years else self.corr_year.setCurrentIndex(len(years)-1))
                self.corr_year.blockSignals(False)

            if hasattr(self, 'rank_combo') and not self.rank_combo.count():
                self.rank_combo.blockSignals(True)
                self.rank_combo.addItems(years)
                self.rank_combo.setCurrentIndex(len(years)-1)
                self.rank_combo.blockSignals(False)

            if hasattr(self, 'combo'):
                map_years = [str(y) for y in sorted(self.df.dropna(subset=['GSYİH'])['Yıl'].unique().tolist())] if 'GSYİH' in self.df.columns else years
                prev_combo = self.combo.currentText()
                self.combo.blockSignals(True); self.combo.clear(); self.combo.addItems(map_years)
                self.combo.setCurrentText(prev_combo) if prev_combo in map_years else self.combo.setCurrentIndex(len(map_years)-1)
                self.combo.blockSignals(False)

            if hasattr(self, 'rd_start'):
                prev_rd_s, prev_rd_e = self.rd_start.currentText(), self.rd_end.currentText()
                self.rd_start.blockSignals(True); self.rd_start.clear(); self.rd_start.addItems(years)
                self.rd_start.setCurrentText(prev_rd_s) if prev_rd_s in years else self.rd_start.setCurrentIndex(0)
                self.rd_start.blockSignals(False)
                self.rd_end.blockSignals(True); self.rd_end.clear(); self.rd_end.addItems(years)
                self.rd_end.setCurrentText(prev_rd_e) if prev_rd_e in years else self.rd_end.setCurrentIndex(len(years)-1)
                self.rd_end.blockSignals(False)

            if hasattr(self, 'blk_year'):
                prev_blk = self.blk_year.currentText()
                self.blk_year.blockSignals(True); self.blk_year.clear(); self.blk_year.addItems(years)
                self.blk_year.setCurrentText(prev_blk) if prev_blk in years else (self.blk_year.setCurrentText('2024') if '2024' in years else self.blk_year.setCurrentIndex(len(years)-1))
                self.blk_year.blockSignals(False)

            try:
                iso = getattr(self, 'current_country_iso', 'TUR')
                y = int(self.combo.currentText())
            except Exception:
                return
            df_y = self.df[self.df['Yıl'] == y].copy()
            row = df_y[df_y['ISO'] == iso]
            if row.empty: return
            r = row.iloc[0]
        
            # Calculate Rank (Safety check added)
            if 'GSYİH' in df_y.columns:
                df_y['Sıra'] = pd.to_numeric(df_y['GSYİH'], errors='coerce').rank(ascending=False, method='min')
                rank_series = df_y.loc[df_y['ISO'] == iso, 'Sıra']
                rank = int(rank_series.values[0]) if not rank_series.empty and pd.notna(rank_series.values[0]) else "-"
            else:
                rank = "-"
        
            def fv(col, fmt='pct', decimals=1):
                """NaN-safe ve tip-güvenli değer formatlayıcı. Her durumda güvenli döner."""
                try:
                    val = r.get(col, np.nan)
                    # Sütun yoksa veya NaN ise N/A döndür
                    if val is None or (not isinstance(val, str) and pd.isna(val)):
                        return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'
                    # String kontrolü — sayıya çevirmeye çalış
                    val = float(val)
                    # inf/nan sonrası kontrol
                    if not np.isfinite(val):
                        return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'
                    if fmt == 'pct':
                        return f'%{val:.{decimals}f}'
                    if fmt == 'usd':
                        return f'${val:,.0f}'
                    if fmt == 'num':
                        return f'{val:,.1f}'
                    if fmt == 'bil':
                        return f'${val/1e9:,.1f} {self.t("bill")}'
                    return f'{val:.{decimals}f}'
                except Exception:
                    return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'

            def fvs(col, fmt='pct', decimals=1):
                """Seyrek veriler için: seçili yılda NaN ise en son geçerli yılı bulur ve gösterir."""
                try:
                    val = r.get(col, np.nan)
                    data_year = y
                    if val is None or (not isinstance(val, str) and pd.isna(val)):
                        # Fallback: o ülkenin bu sütundaki son geçerli satırını bul
                        iso_val = r.get('ISO', None)
                        if iso_val and col in self.df.columns:
                            hist = self.df[(self.df['ISO'] == iso_val) & (self.df[col].notna())].sort_values('Yıl')
                            if not hist.empty:
                                val = hist[col].iloc[-1]
                                data_year = int(hist['Yıl'].iloc[-1])
                            else:
                                return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'
                        else:
                            return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'
                    val = float(val)
                    if not np.isfinite(val):
                        return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'
                    if fmt == 'pct':
                        formatted = f'%{val:.{decimals}f}'
                    elif fmt == 'usd':
                        formatted = f'${val:,.0f}'
                    elif fmt == 'num':
                        formatted = f'{val:,.1f}'
                    elif fmt == 'bil':
                        formatted = f'${val/1e9:,.1f} {self.t("bill")}'
                    else:
                        formatted = f'{val:.{decimals}f}'
                    # Eğer farklı bir yıldan veri geldiyse yılı belirt
                    if data_year != y:
                        return f'{formatted} <span style="color:#7f8c8d; font-size:10px; font-style:italic;">({data_year})</span>'
                    return formatted
                except Exception:
                    return '<span style="color:#95a5a6; font-style:italic;">N/A</span>'

            def grw_color(col):
                try:
                    val = float(r.get(col, np.nan))
                    if not np.isfinite(val): return '#95a5a6'
                    return '#27ae60' if val > 0 else '#c0392b'
                except Exception:
                    return '#95a5a6'

            def inf_color(col):
                try:
                    val = float(r.get(col, np.nan))
                    if not np.isfinite(val): return '#2c3e50'
                    return '#c0392b' if val > 15 else '#2c3e50'
                except Exception:
                    return '#2c3e50'

            country_display = self._display_country(r['Ülke'])
            # Reel sütun varlık kontrolü — eski parquet dosyalarında bulunmayabilir
            _gdp_reel_col  = 'GSYİH (Reel)' if 'GSYİH (Reel)' in r.index else 'GSYİH'
            _gsmh_reel_col = 'GSMH (Reel)'  if 'GSMH (Reel)'  in r.index else 'GSMH'
            _gdp_reel_lbl  = '' if _gdp_reel_col  == 'GSYİH (Reel)' else '(Nominal)'
            _gsmh_reel_lbl = '' if _gsmh_reel_col == 'GSMH (Reel)'  else '(Nominal)'
            html = f"""
            <div style="font-family:'Segoe UI',sans-serif; color:#2c3e50; line-height:1.6; padding:10px;">
                <div style="font-size:24px; font-weight:bold; border-bottom:4px solid #1a5276; margin-bottom:15px; padding-bottom:8px; color:#1a5276;">{country_display} ({y})</div>
            
                <div style="background:#f0f4f8; padding:15px; border-radius:10px; border-left:6px solid #1a5276; margin-bottom:20px;">
                    <b style="font-size:18px; color:#1a5276;">{self.t('glob_perf')}</b><br>
                    <div style="margin-top:8px;">
                        &bull; {self.t('gdp_rank')}: <b style="color:#c0392b;">#{rank}</b><br>
                        &bull; {self.t('gdp_nom')}: <b>{fv(_gdp_reel_col, 'bil')}</b> <span style="font-size:11px; color:#2980b9; font-style:italic;">{_gdp_reel_lbl}</span><br>
                        &bull; {self.t('gni_nom')}: <b>{fv(_gsmh_reel_col, 'bil')}</b> <span style="font-size:11px; color:#2980b9; font-style:italic;">{_gsmh_reel_lbl}</span><br>
                        &bull; {self.t('gdp_pc_reel')}: <b>{fv('Kişi Başı GSYİH (Reel)', 'usd')}</b><br>
                        &bull; {self.t('gdp_pc_sagp')}: <b>{fv('Kişi Başı GSYİH (SAGP)', 'usd')}</b><br>
                        &bull; {self.t('gni_pc_reel')}: <b>{fv('Kişi Başı GSMH (Reel)', 'usd')}</b><br>
                        &bull; {self.t('gni_pc_sagp')}: <b>{fv('Kişi Başı GSMH (SAGP)', 'usd')}</b>
                    </div>
                </div>
            
                <div style="margin-bottom:20px;">
                    <b style="font-size:16px; color:#1a5276;">{self.t('sec_dist')}</b><br>
                    <div style="margin-top:8px; padding-left:10px;">
                        &bull; {self.t('sec_agr')}: <b>{fv('Tarım')}</b><br>
                        &bull; {self.t('sec_ind')}: <b>{fv('Sanayi')}</b><br>
                        &bull; {self.t('sec_srv')}: <b>{fv('Hizmetler')}</b>
                    </div>
                </div>
            
                <div style="margin-bottom:20px;">
                    <b style="font-size:16px; color:#1a5276;">{self.t('conj')}</b><br>
                    <div style="margin-top:8px; padding-left:10px;">
                        &bull; {self.t('grw')}: <span style="font-weight:bold; color:{grw_color('Büyüme')};">{fv('Büyüme')}</span><br>
                        &bull; {self.t('inf')}: <span style="font-weight:bold; color:{inf_color('Enflasyon')};">{fv('Enflasyon')}</span><br>
                        &bull; {self.t('ppi')}: <b>{fv('PPI', 'num', 1)}</b><br>
                        &bull; {self.t('ipi')}: <b>{fv('IPI', 'num', 1)}</b><br>
                        &bull; {self.t('unemp')}: <b>{fv('İşsizlik')}</b><br>
                        &bull; {self.t('cab')}: <b>{fv('Cari Denge')}</b>
                    </div>
                </div>
            
                <div style="margin-bottom:20px; background:#ebf5fb; padding:12px; border-radius:10px; border-left:6px solid #2980b9;">
                    <b style="font-size:16px; color:#154360;">{self.t('pub')}</b><br>
                    <div style="margin-top:8px;">
                        &bull; {self.t('kamu_harc')}: <b>{fv('Kamu Harcamaları')}</b><br>
                        &bull; {self.t('sav_harc')}: <b>{fv('Savunma Harcamaları')}</b><br>
                        &bull; {self.t('egitim')}: <b>{fv('Eğitim')}</b><br>
                        &bull; {self.t('saglik')}: <b>{fv('Sağlık')}</b><br>
                        &bull; {self.t('vergi_gel')}: <b>{fv('Vergi Gelirleri')}</b><br>
                        &bull; {self.t('butce_deng')}: <b>{fv('Bütçe Dengesi')}</b><br>
                        &bull; {self.t('dis_borc')}: <b>{fv('Dış Borç')}</b><br>
                        &bull; {self.t('sosyal_ref')}: <b>{fv('Sosyal Refah')}</b>
                    </div>
                </div>

                <div style="background:#fef9e7; padding:12px; border-radius:10px; border-left:6px solid #f1c40f;">
                    <b style="font-size:16px; color:#7d6608;">{self.t('hc')}</b><br>
                    <div style="margin-top:8px;">
                        &bull; {self.t('hdi')}: <b>{fvs('HDI_UNDP', 'num', 3)}</b><br>
                        &bull; {self.t('ihdi')}: <b>{fvs('IHDI', 'num', 2)}</b><br>
                        &bull; {self.t('phdi')}: <b>{fvs('PHDI', 'num', 2)}</b><br>
                        &bull; {self.t('gii')}: <b>{fvs('GII', 'num', 2)}</b><br>
                        &bull; {self.t('gdi')}: <b>{fvs('GDI', 'num', 2)}</b><br>
                        &bull; {self.t('lit')}: <b>{fvs('Okuryazarlık')}</b><br>
                        &bull; {self.t('gini')}: <b>{fvs('Gini', 'num')}</b><br>
                        &bull; {self.t('palma_ratio')}: <b>{fv('palma_ratio', 'num', 2)}</b><br>
                        &bull; {self.t('wiid_s10s1_ratio')}: <b>{fv('WIID_Ratio', 'num', 1)}</b>
                    </div>
                </div>
            </div>
            """
            try:
                self.li.setHtml(html)
                if hasattr(self, 'li_map'): self.li_map.setHtml(html)
            except Exception as _e:
                print(f"[ui_refresh] HTML render hata: {_e}")

    def _resolve_ind(self, display_name):
            """Display adından gerçek sütun adına çevirir."""
            if hasattr(self, '_ind_display') and hasattr(self, '_ind_keys'):
                try:
                    idx = self._ind_display.index(display_name)
                    return self._ind_keys[idx]
                except ValueError:
                    pass
            # Blk_cmb için ters dönüş
            blk_display = self.langs[self.current_lang].get('blk_display', [])
            blk_items = self.langs[self.current_lang].get('blk_items', [])
            if display_name in blk_display:
                try: return blk_items[blk_display.index(display_name)]
                except: pass
            return display_name

    def toggle_theme(self):
            self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
            self.btn_theme_toggle.setText("☀️ Aydınlık Mod" if self.current_theme == 'dark' else "🌙 Karanlık Mod")
            self.apply_app_theme(); self.update_map()

    def apply_app_theme(self):
            t = self.themes[self.current_theme]
            qss = f"""
            QMainWindow {{ background-color: {t['bg']}; }}
            QComboBox {{
                background-color: {t['card']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 2px 4px;
                min-width: 55px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['card']};
                color: {t['text']};
                border: 1px solid {t['border']};
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }}
            """
            self.setStyleSheet(qss)
            self.sidebar.setStyleSheet(f"background-color: {t['sidebar']}; color: white; border:none;")
            self.logo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: { '#ecf0f1' if self.current_theme=='light' else '#eee' }; border-bottom: 2px solid { '#34495e' if self.current_theme=='light' else '#444' }; padding-bottom: 10px;")
        
            self.switch_page(self.stacked_widget.currentIndex())

    def get_nav_style(self, active):
            t = self.themes[self.current_theme]
            base = "QPushButton { border: none; font-size: 15px; font-weight: bold; text-align: left; padding: 12px; border-radius: 5px; margin-bottom: 5px; "
            if active: return base + f"background-color: #3498db; color: white; }}"
            return base + f"background-color: transparent; color: { '#bdc3c7' if self.current_theme=='light' else '#7f8c8d' }; }} QPushButton:hover {{ background-color: #2980b9; color: white; }}"

    def switch_language(self):
            self.current_lang = 'en' if self.current_lang == 'tr' else 'tr'
            self.btn_lang_toggle.setText("🇹🇷 Türkçe" if self.current_lang == 'en' else "🌐 English")
            self.apply_translations()
            if self.df is not None:
                self.ui_refresh()
                self.update_map()
                self.plot_macro()
                self.update_risk()
                self.plot_blocks()

    def apply_translations(self):
            self.setWindowTitle(self.t('title'))
            self.logo.setText(self.t('logo'))
            self.update_btn.setText(self.t('update_btn'))
        
            self.btn_nav_map.setText(self.t('nav_map'))
            if hasattr(self, 'btn_nav_macro'): self.btn_nav_macro.setText(self.t('nav_macro'))
            self.btn_nav_rd.setText(self.t('nav_rd'))
            if hasattr(self, 'btn_nav_block'): self.btn_nav_block.setText(self.t('nav_block'))
            self.btn_nav_sector.setText(self.t('nav_sector'))
            if hasattr(self, 'btn_nav_energy'): self.btn_nav_energy.setText(self.t('nav_energy'))
        
            tm = 'theme_light' if self.current_theme == 'dark' else 'theme_dark'
            self.btn_theme_toggle.setText(self.t(tm))
        
            if hasattr(self, 'search_combo'): self.search_combo.setPlaceholderText(self.t('search_placeholder'))
            if hasattr(self, 'lbl_energy_sources'): self.lbl_energy_sources.setText(self.t('energy_source_text'))
            if hasattr(self, 'lbl_statik'): self.lbl_statik.setText(self.t('statik_yil'))
            if hasattr(self, 'bu'): self.bu.setText(self.t('refresh_btn'))
            if hasattr(self, 'bc'): self.bc.setText(self.t('clear_btn'))
            if hasattr(self, 'btn_copy'): self.btn_copy.setText(self.t('copy_btn'))
        
            if hasattr(self, 'lbl_rank_t'): self.lbl_rank_t.setText(self.t('rank_title'))
            if hasattr(self, 'lbl_yil_sec'): self.lbl_yil_sec.setText(self.t('yil_sec'))
            if hasattr(self, 'rw_tbl'): self.rw_tbl.setHorizontalHeaderLabels([self.t('rank_h1'), self.t('rank_h2'), self.t('rank_h3'), self.t('rank_h4')]) 
        
            if hasattr(self, 'lbl_ts_c'): self.lbl_ts_c.setText(self.t('country_lbl'))
            if hasattr(self, 'lbl_ts_ind'): self.lbl_ts_ind.setText(self.t('ind_lbl'))
            if hasattr(self, 'lbl_ts_price'): self.lbl_ts_price.setText(self.t('price_type_lbl'))
            if hasattr(self, 'lbl_ts_base'): self.lbl_ts_base.setText(self.t('base_year_lbl'))
            if hasattr(self, 'lbl_ts_per'): self.lbl_ts_per.setText(self.t('period_lbl'))
            if hasattr(self, 'lbl_pub_per'): self.lbl_pub_per.setText(self.t('period_lbl'))
            if hasattr(self, 'lbl_pub_c'): self.lbl_pub_c.setText(self.t('country_lbl'))
            if hasattr(self, 'btn_nav_pub'): self.btn_nav_pub.setText(self.t('nav_pub'))
            if hasattr(self, 'lbl_pub_ind'): self.lbl_pub_ind.setText(self.t('ind_lbl'))
            if hasattr(self, 'pub_ind'):
                self.pub_ind.blockSignals(True)
                self.pub_ind.clear()
                items_tr = ["Kamu Harcamaları", "Eğitim Harcamaları", "Sağlık Harcamaları", "Savunma Harcamaları", "Vergi Gelirleri", "Bütçe Dengesi", "Dış Borç", "Cari Denge"]
                items_en = ["Gov Expenditure", "Education Exp.", "Health Exp.", "Military Exp.", "Tax Revenue", "Budget Balance", "External Debt", "Current Account"]
                items = items_tr if self.current_lang == 'tr' else items_en
                self.pub_ind.addItems(items)
                for i in range(self.pub_ind.count()):
                    it = self.pub_ind.model().item(i)
                    if it: it.setCheckState(Qt.Checked if i < 3 else Qt.Unchecked)
                self.pub_ind.blockSignals(False)
            
        
            if hasattr(self, 'lbl_rd_c1'): self.lbl_rd_c1.setText(self.t('country1_lbl'))
            if hasattr(self, 'lbl_rd_c2'): self.lbl_rd_c2.setText(self.t('country2_lbl'))
            if hasattr(self, 'btn_export_risk'): self.btn_export_risk.setText(self.t('risk_report_btn'))
        
            # CheckableComboBox placeholder metnini dile göre güncelle
            _ph = "--- Please Select ---" if self.current_lang == 'en' else "--- Seçim Yapınız ---"
            _also = " (+{n} more)" if self.current_lang == 'en' else " (+{n} daha)"
            for attr in ['macro_c', 'macro_cmb', 'ts_country', 'rd_country1', 'sec_c', 'sec_ind', 'risk_c', 'risk_ind', 'pub_c', 'pub_ind', 'corr_c']:
                cb = getattr(self, attr, None)
                if cb and hasattr(cb, 'setPlaceholder'):
                    cb.setPlaceholder(_ph)
                    cb.update()
            if hasattr(self, 'rd_table'): self.rd_table.setHorizontalHeaderLabels([self.t('risk_h1'), self.t('risk_h2'), self.t('risk_h3'), self.t('risk_h4')])
            if hasattr(self, 'lbl_welfare'): self.lbl_welfare.setText(self.t('nav_rd'))
        
            if hasattr(self, 'lbl_macro_c'):   self.lbl_macro_c.setText(self.t('country_lbl'))
            if hasattr(self, 'lbl_macro_per'):  self.lbl_macro_per.setText(self.t('period_lbl'))
            if hasattr(self, 'lbl_macro_ind'):   self.lbl_macro_ind.setText(self.t('ind_sel_lbl'))
            if hasattr(self, 'lbl_macro_price'): self.lbl_macro_price.setText(self.t('price_type_lbl'))
        
            if hasattr(self, 'btn_macro_mode'): self.btn_macro_mode.setText(self.t('mode_period') if self.macro_mode == "instant" else self.t('mode_instant'))
            if hasattr(self, 'btn_pub_mode'): self.btn_pub_mode.setText(self.t('mode_period') if self.pub_mode == "instant" else self.t('mode_instant'))
        
            if hasattr(self, 'macro_cmb'):
                cur = self.macro_cmb.currentText()
                self.macro_cmb.blockSignals(True)
                self.macro_cmb.clear()
                items_tr = ["GSYİH", "GSMH", "Enflasyon", "Büyüme", "İşsizlik", "Kişi Başı GSYİH", "Kişi Başı GSMH", "Kişi Başı GSYİH (SAGP)", "Kişi Başı GSMH (SAGP)", "Cari Denge", "Borç Oranı", "Kişi Başı Enerji (kWh)", "Fosil Yakıt Payı (%)", "Yenilenebilir Payı (%)", "Karbon (Milyon Ton)", "Kişi Başı Karbon (Ton)", "Enerji İthalatı Bağımlılığı"]
                items_en = ["GDP", "GNI", "Inflation", "Growth", "Unemployment", "GDP Per Capita", "GNI Per Capita", "GDP Per Capita (PPP)", "GNI Per Capita (PPP)", "Current Account", "Debt Ratio", "Energy Per Capita (kWh)", "Fossil Fuel Share (%)", "Renewables Share (%)", "Carbon (Million Tonnes)", "Carbon Per Capita (Tonnes)", "Energy Imports"]
                items = items_tr if self.current_lang == 'tr' else items_en
                self.macro_cmb.addItems(items)
                if cur in items: self.macro_cmb.setCurrentText(cur)
                else:
                    # Try to map TR to EN or vice versa
                    mapping_tr_to_en = dict(zip(items_tr, items_en))
                    mapping_en_to_tr = dict(zip(items_en, items_tr))
                    if self.current_lang == 'en' and cur in mapping_tr_to_en: self.macro_cmb.setCurrentText(mapping_tr_to_en[cur])
                    elif self.current_lang == 'tr' and cur in mapping_en_to_tr: self.macro_cmb.setCurrentText(mapping_en_to_tr[cur])
                self.macro_cmb.blockSignals(False)

            if hasattr(self, 'macro_price'):
                cur = self.macro_price.currentText()
                self.macro_price.blockSignals(True)
                self.macro_price.clear()
                self.macro_price.addItems(["Nominal", "Reel"] if self.current_lang == 'tr' else ["Nominal", "Real"])
                if cur in ["Reel", "Real"]: self.macro_price.setCurrentText("Reel" if self.current_lang == 'tr' else "Real")
                else: self.macro_price.setCurrentText("Nominal")
                self.macro_price.blockSignals(False)



            # Dil değişiminde tüm grafikleri güncelle
            if hasattr(self, 'df') and self.df is not None:
                try: self.plot_macro()
                except: pass
                try: self.draw_pub_chart()
                except: pass
                try: self.draw_sectoral_chart()
                except: pass
                try: self.draw_risk_chart()
                except: pass
                try: self.draw_corr_chart()
                except: pass
        
            if hasattr(self, 'lbl_blk_ind'): self.lbl_blk_ind.setText(self.t('ind_sel_lbl'))
            if hasattr(self, 'lbl_blk_year'): self.lbl_blk_year.setText(self.t('year') + ":")
            if hasattr(self, 'lbl_blk_price'): self.lbl_blk_price.setText(self.t('price_type_lbl'))
        
            if hasattr(self, 'blk_price'):
                cur = self.blk_price.currentText()
                self.blk_price.blockSignals(True)
                self.blk_price.clear()
                self.blk_price.addItems(["Reel", "Nominal"] if self.current_lang == 'tr' else ["Real", "Nominal"])
                if cur in ["Reel", "Real"]: self.blk_price.setCurrentText("Reel" if self.current_lang == 'tr' else "Real")
                else: self.blk_price.setCurrentText("Nominal")
                self.blk_price.blockSignals(False)
            
            if hasattr(self, 'lbl_sec_c'): self.lbl_sec_c.setText(self.t('country_lbl'))
            if hasattr(self, 'lbl_sec_per'): self.lbl_sec_per.setText(self.t('period_lbl'))
            if hasattr(self, 'lbl_sec_ind'): self.lbl_sec_ind.setText(self.t('ind_lbl'))
            if hasattr(self, 'sec_ind'):
                cur_checked = self.sec_ind.checkedItems()
                # We need to re-populate it with translated items while keeping selection
                # But simpler is to just use the mapping in the chart function and keep display items
                # However, for consistency, let's translate the items
                self.sec_ind.blockSignals(True)
                self.sec_ind.clear()
                items_tr = ["Tarım Payı", "Sanayi Payı", "Hizmetler Payı", "İmalat Payı", "Enerji-Maden", "Demir-Çelik", "Otomotiv-Makine", "Lojistik", "Bilgi-İletişim", "Finans-Sigorta"]
                items_en = ["Agriculture Share", "Industry Share", "Services Share", "Manufacturing Share", "Energy-Mining", "Iron-Steel", "Automotive-Machinery", "Logistics", "ICT Services", "Finance-Insurance"]
                items = items_tr if self.current_lang == 'tr' else items_en
                self.sec_ind.addItems(items)
                for i in range(self.sec_ind.count()):
                    it = self.sec_ind.model().item(i)
                    if it: it.setCheckState(Qt.Checked if i < 3 else Qt.Unchecked)
                self.sec_ind.blockSignals(False)
            
            if hasattr(self, 'btn_nav_risk'): self.btn_nav_risk.setText(self.t('nav_risk'))
            if hasattr(self, 'lbl_risk_c'): self.lbl_risk_c.setText(self.t('country_lbl'))
            if hasattr(self, 'lbl_risk_per'): self.lbl_risk_per.setText(self.t('period_lbl'))
            if hasattr(self, 'lbl_risk_ind'): self.lbl_risk_ind.setText(self.t('ind_lbl'))
            if hasattr(self, 'lbl_energy_c'): self.lbl_energy_c.setText(self.t('country_lbl'))
            if hasattr(self, 'lbl_energy_per'): self.lbl_energy_per.setText(self.t('period_lbl'))
            if hasattr(self, 'btn_export_energy'): self.btn_export_energy.setText(self.t('report_btn'))
            
            if hasattr(self, 'risk_ind'):
                self.risk_ind.blockSignals(True)
                self.risk_ind.clear()
                items_tr = ["Cari İşlemler Dengesi", "Toplam Dış Borç Stoku", "Ülke Risk Primi (Proxy)", 
                            "İthalat Karşılama Süresi", "Kısa Vadeli Borç / Rezerv", "DYY Girişi", 
                            "Reel Efektif Kur (REK)", "Reel Faiz Oranı", "Bütçe Dengesi", "Borç Servisi"]
                items_en = ["Current Account Balance", "External Debt Stock", "Risk Premium (Proxy)", 
                            "Import Cover (Months)", "ST Debt / Reserves", "FDI Inflow", 
                            "REER Index", "Real Interest Rate", "Budget Balance", "Debt Service"]
                items = items_tr if self.current_lang == 'tr' else items_en
                self.risk_ind.addItems(items)
                for i in range(self.risk_ind.count()):
                    it = self.risk_ind.model().item(i)
                    if it: it.setCheckState(Qt.Checked if i < 4 else Qt.Unchecked)
                self.risk_ind.blockSignals(False)
            
            # Retranslate blk_cmb, ts_ind and bm_ind if already populated
            ind_names = self.langs[self.current_lang].get('ind_names', {})
            if hasattr(self, '_ind_keys'):
                inds_display = [ind_names.get(c, c) for c in self._ind_keys]
                self._ind_display = inds_display
                for cmb in [self.blk_cmb, self.corr_x, self.corr_y]:
                    cur = cmb.currentText()
                    cmb.blockSignals(True); cmb.clear(); cmb.addItems(inds_display); cmb.blockSignals(False)
                    # Restore closest match
                    if cur in inds_display: cmb.setCurrentText(cur)
        
            if hasattr(self, 'lbl_ineq'): self.lbl_ineq.setText(self.t('ineq_chart_hdr'))
            if hasattr(self, 'lbl_bullet'): self.lbl_bullet.setText(self.t('bullet_chart_title'))
        
        
        
            # Ülke listelerini yeniden çevir
            if hasattr(self, '_country_en_list') and self._country_en_list:
                sorted_names = sorted([self._display_country(n) for n in self._country_en_list], key=self._sort_key)
                clist = [self.t('no_country')] + sorted_names
                cur_iso = getattr(self, 'current_country_iso', None)
                for cmb in [self.rd_country1, self.rd_country2, self.search_combo, self.pub_c, self.sec_c, self.risk_c, getattr(self, 'energy_country', None)]:
                    if cmb is None: continue
                    cur_val = cmb.currentText()
                    cmb.blockSignals(True); cmb.clear(); cmb.addItems(clist); cmb.blockSignals(False)
                if cur_iso and self.df is not None:
                    matches = self.df[self.df['ISO'] == cur_iso]['Ülke']
                    if not matches.empty:
                        self.search_combo.blockSignals(True)
                        self.search_combo.setCurrentText(self._display_country(matches.iloc[0]))
                        self.search_combo.blockSignals(False)
                cm = QCompleter(clist); cm.setCaseSensitivity(Qt.CaseInsensitive)
                self.search_combo.setCompleter(cm)