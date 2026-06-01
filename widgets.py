"""
widgets.py — Özel PyQt5 widget sınıfları
CheckableComboBox, GaugeCanvas, CustomWebPage
"""
import plotly.graph_objects as go

from PyQt5.QtWidgets import (QComboBox, QListView, QStylePainter,
                              QStyleOptionComboBox, QStyle)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from sbf_terminal.utils import _load_plotly_to_view


# ── CustomWebPage ─────────────────────────────────────────────────────────────
class CustomWebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "select":
            iso = url.host()
            self.parent().on_country_selected(iso)
            return False
        return True


# ── GaugeCanvas ───────────────────────────────────────────────────────────────
class GaugeCanvas(QWebEngineView):
    def __init__(self, parent=None, width=3, height=2, dpi=90):
        super().__init__(parent)
        self.fig = go.Figure()
        self.fig.update_layout(
            paper_bgcolor='#fafafa',
            margin=dict(l=20, r=20, t=20, b=20)
        )
        self.update_view()

    def update_view(self):
        _load_plotly_to_view(self, self.fig)

    def draw_gauge(self, value, title, is_debt=True, ax=None):
        import pandas as pd
        try:
            self.fig = go.Figure()
            if pd.isna(value):
                self.fig.add_annotation(
                    text="Veri Yok", xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=12, color='#7f8c8d')
                )
            else:
                if is_debt:
                    colors = ['#27ae60', '#f1c40f', '#e74c3c']
                    range_limits = [0, 40, 60, 100]
                else:
                    colors = ['#e74c3c', '#f1c40f', '#27ae60']
                    range_limits = [-10, -5, 0, 10]
                self.fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    title={'text': title, 'font': {'size': 10, 'color': '#2c3e50'}},
                    gauge={
                        'axis': {'range': [range_limits[0], range_limits[-1]]},
                        'bar': {'color': "black", 'thickness': 0.2},
                        'steps': [
                            {'range': [range_limits[0], range_limits[1]], 'color': colors[0]},
                            {'range': [range_limits[1], range_limits[2]], 'color': colors[1]},
                            {'range': [range_limits[2], range_limits[3]], 'color': colors[2]}
                        ]
                    }
                ))
            self.fig.update_layout(
                paper_bgcolor='#fafafa',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            self.update_view()
        except Exception as e:
            print("Gauge Hatası:", e)


# ── CheckableComboBox ─────────────────────────────────────────────────────────
class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self._placeholder = "--- Seçim Yapınız ---"

    def setPlaceholder(self, text):
        self._placeholder = text
        self.update()

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.update()
        self.currentTextChanged.emit(self.currentText())

    def checkedItems(self):
        checked = []
        for i in range(self.count()):
            item = self.model().item(i)
            if item and item.checkState() == Qt.Checked:
                checked.append(self.itemText(i))
        return checked

    def clearSelection(self):
        changed = False
        for i in range(self.count()):
            item = self.model().item(i)
            if item and item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
                changed = True
        if changed:
            self.update()
            self.currentTextChanged.emit(self.currentText())

    def addItem(self, text, userData=None):
        super().addItem(text, userData)
        item = self.model().item(self.count() - 1, 0)
        if item:
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

    def addItems(self, texts):
        for text in texts:
            self.addItem(text)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        checked = self.checkedItems()
        if len(checked) == 0:
            opt.currentText = self._placeholder
        elif len(checked) == 1:
            opt.currentText = checked[0]
        elif len(checked) == 2:
            opt.currentText = f"{checked[0]}, {checked[1]}"
        else:
            opt.currentText = f"{checked[0]}, {checked[1]} (+{len(checked)-2})"
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)
