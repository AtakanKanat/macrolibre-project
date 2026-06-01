"""
page_energy.py — Mixin: Enerji Ekonomisi (Page 10)
Enerji tüketimi, üretim kaynakları (Fosil vs Yenilenebilir) ve CO2 emisyon analizleri.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from sbf_terminal.utils import _load_plotly_to_view

class EnergyMixin:
    """Page 10 — Enerji Ekonomisi."""
    
    def update_energy(self):
        try:
            if self.df is None:
                return
            c_displays = self.energy_country.checkedItems() if hasattr(self.energy_country, 'checkedItems') else [self.energy_country.currentText()]
            c_displays = [c for c in c_displays if c and not c.startswith('---')]
            if not c_displays:
                return
            
            try:
                y_start = int(self.energy_start.currentText()) if hasattr(self, 'energy_start') and self.energy_start.currentText() else 2000
                y_end = int(self.energy_end.currentText()) if hasattr(self, 'energy_end') and self.energy_end.currentText() else 2024
            except Exception:
                y_start, y_end = 2000, 2024
            
            if y_start > y_end:
                y_start, y_end = y_end, y_start
                
            self.draw_energy_charts(c_displays, y_start, y_end)
            
        except Exception as e:
            print(f"[update_energy] Hata: {e}")

    def draw_energy_charts(self, c_displays, y_start, y_end):
        if not hasattr(self, 'energy_web1') or not hasattr(self, 'energy_web2') or not hasattr(self, 'energy_web3'):
            return
            
        is_en = getattr(self, 'current_lang', 'tr') == 'en'
        
        pf1 = go.Figure() # Mutlak/Göreli Ayrışma (Decoupling)
        pf2 = go.Figure() # Karbondan Arındırma (100% Stacked Area)
        pf3 = go.Figure() # Enerji İthalatı Bağımlılığı (Risk Threshold)
        
        has_data1 = False
        has_data2 = False
        has_data3 = False
        
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22']
        
        for ci, c_lbl in enumerate(c_displays):
            c = self._en_country(c_lbl)
            if not c:
                continue
            df_c = self.df[(self.df['Ülke'] == c) & (self.df['Yıl'] >= y_start) & (self.df['Yıl'] <= y_end)].sort_values('Yıl')
            cn = self._display_country(c)
            base_clr = colors[ci % len(colors)]
            
            # --- Grafik 1: Mutlak/Göreli Ayrışma (Decoupling) ---
            # Sol Eksen: GSYİH, Sağ Eksen: Enerji Yoğunluğu
            gdp_col = 'Kişi Başı GSYİH (Reel)' if 'Kişi Başı GSYİH (Reel)' in df_c.columns else 'Kişi Başı GSYİH'
            if gdp_col in df_c.columns and not df_c[gdp_col].dropna().empty:
                df_col = df_c.dropna(subset=[gdp_col])
                pf1.add_trace(go.Scatter(
                    x=df_col['Yıl'], y=df_col[gdp_col],
                    mode='lines',
                    name=f"{cn} — {'GDP per Capita' if is_en else 'Kişi Başı GSYİH'}",
                    line=dict(color=base_clr, width=3, dash='solid'),
                    yaxis='y1'
                ))
                has_data1 = True
                
            if 'Kişi Başı Enerji (kWh)' in df_c.columns and not df_c['Kişi Başı Enerji (kWh)'].dropna().empty:
                df_col = df_c.dropna(subset=['Kişi Başı Enerji (kWh)'])
                pf1.add_trace(go.Scatter(
                    x=df_col['Yıl'], y=df_col['Kişi Başı Enerji (kWh)'],
                    mode='lines',
                    name=f"{cn} — {'Energy (kWh)' if is_en else 'Enerji (kWh)'}",
                    line=dict(color=base_clr, width=2, dash='dot'),
                    yaxis='y2'
                ))
                has_data1 = True

            # --- Grafik 2: Karbondan Arındırma (100% Stacked Area) ---
            # Stackgroup='one' and groupnorm='percent' creates 100% stacked area chart
            if 'Fosil Yakıt Payı (%)' in df_c.columns and not df_c['Fosil Yakıt Payı (%)'].dropna().empty:
                df_col = df_c.dropna(subset=['Fosil Yakıt Payı (%)'])
                pf2.add_trace(go.Scatter(
                    x=df_col['Yıl'], y=df_col['Fosil Yakıt Payı (%)'],
                    mode='lines', stackgroup='one', groupnorm='percent',
                    name=f"{cn} — {'Fossil (%)' if is_en else 'Fosil (%)'}",
                    line=dict(width=0.5, color='#7f8c8d'),
                    fillcolor='rgba(127, 140, 141, 0.8)'
                ))
                has_data2 = True
                
            if 'Yenilenebilir Payı (%)' in df_c.columns and not df_c['Yenilenebilir Payı (%)'].dropna().empty:
                df_col = df_c.dropna(subset=['Yenilenebilir Payı (%)'])
                pf2.add_trace(go.Scatter(
                    x=df_col['Yıl'], y=df_col['Yenilenebilir Payı (%)'],
                    mode='lines', stackgroup='one', groupnorm='percent',
                    name=f"{cn} — {'Renewable (%)' if is_en else 'Yenilenebilir (%)'}",
                    line=dict(width=0.5, color='#27ae60'),
                    fillcolor='rgba(39, 174, 96, 0.8)'
                ))
                has_data2 = True

            # --- Grafik 3: Stratejik Bağımlılık (Enerji İthalatı Bağımlılığı) ---
            if 'Enerji İthalatı Bağımlılığı' in df_c.columns and not df_c['Enerji İthalatı Bağımlılığı'].dropna().empty:
                df_col = df_c.dropna(subset=['Enerji İthalatı Bağımlılığı'])
                # Kırmızı gölgelendirme için %50 üzerini boyama mantığı
                y_vals = df_col['Enerji İthalatı Bağımlılığı'].values
                x_vals = df_col['Yıl'].values
                pf3.add_trace(go.Scatter(
                    x=x_vals, y=y_vals,
                    mode='lines+markers',
                    name=f"{cn}",
                    line=dict(color=base_clr, width=2),
                    marker=dict(size=6)
                ))
                # Add threshold fill logic: Plotly doesn't natively fill "only above Y".
                # But we can add a horizontal shape for the threshold.
                has_data3 = True

        # Layout for Chart 1 (Decoupling)
        if not has_data1:
            msg = 'No data found.' if is_en else 'Veri bulunamadı.'
            pf1.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False)
        
        pf1.update_layout(
            title=dict(text='Energy Decoupling: GDP vs Energy Consumption' if is_en else 'Ayrışma (Decoupling): GSYİH ve Enerji Tüketimi', font=dict(size=12, color='#2c3e50')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1', tickangle=-45, dtick=5),
            yaxis=dict(title='GDP per Capita ($)' if is_en else 'Kişi Başı GSYİH ($)', showgrid=True, gridcolor='#ecf0f1', side='left'),
            yaxis2=dict(title='Energy (kWh)' if is_en else 'Enerji (kWh)', overlaying='y', side='right', showgrid=False),
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=45, r=45, t=40, b=40),
            hovermode='x unified', legend=dict(orientation='h', y=-0.2, font=dict(size=10))
        )
        
        # Layout for Chart 2 (Transition)
        if not has_data2:
            msg = 'No data found.' if is_en else 'Veri bulunamadı.'
            pf2.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False)
            
        pf2.update_layout(
            title=dict(text='Energy Transition: Fossil vs Renewable' if is_en else 'Karbondan Arındırma: Enerji Üretim Kaynakları', font=dict(size=12, color='#2c3e50')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1', tickangle=-45, dtick=5),
            yaxis=dict(title='Share (%)' if is_en else 'Pay (%)', showgrid=True, gridcolor='#ecf0f1', range=[0, 100]),
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=45, r=45, t=40, b=40),
            hovermode='x unified', legend=dict(orientation='h', y=-0.2, font=dict(size=10))
        )

        # Layout for Chart 3 (Dependency)
        if not has_data3:
            msg = 'No data found.' if is_en else 'Veri bulunamadı.'
            pf3.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False)
        else:
            pf3.add_shape(
                type="line", x0=y_start, x1=y_end, y0=50, y1=50,
                line=dict(color="red", width=2, dash="dash"),
            )
            pf3.add_annotation(
                x=y_end, y=52,
                text="Structural Risk Threshold (50%)" if is_en else "Yapısal Risk Eşiği (%50)",
                showarrow=False, font=dict(color="red", size=10), xanchor="right"
            )
            # Shade area above 50%
            pf3.add_shape(
                type="rect",
                x0=y_start, x1=y_end,
                y0=50, y1=100, # Assuming max dependency is around 100%
                fillcolor="rgba(231, 76, 60, 0.1)",
                layer="below", line_width=0,
            )
            
        pf3.update_layout(
            title=dict(text='Strategic Dependency: Net Energy Imports (%)' if is_en else 'Stratejik Bağımlılık: Net Enerji İthalatı (%)', font=dict(size=12, color='#2c3e50')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1', tickangle=-45, dtick=5),
            yaxis=dict(title='Imports / Energy Use (%)' if is_en else 'İthalat / Enerji Kullanımı (%)', showgrid=True, gridcolor='#ecf0f1'),
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=45, r=45, t=40, b=40),
            hovermode='x unified', legend=dict(orientation='h', y=-0.2, font=dict(size=10))
        )
        
        _load_plotly_to_view(self.energy_web1, pf1)
        _load_plotly_to_view(self.energy_web2, pf2)
        _load_plotly_to_view(self.energy_web3, pf3)
        
    def export_energy_pdf(self):
        QMessageBox.information(self, "Bilgi", "PDF aktarım özelliği yapım aşamasındadır.")
