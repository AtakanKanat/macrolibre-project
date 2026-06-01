"""
page_devdist.py — Mixin: Kalkınma & Bölüşüm (Page 3)
update_risk, draw_welfare_chart, draw_inequality_chart, export_risk_pdf
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from sbf_terminal.utils import _load_plotly_to_view


class DevDistMixin:
    """Page 3 — Kalkınma & Bölüşüm."""

    def update_risk(self):
        try:
            if self.df is None:
                return
            c_displays = self.rd_country1.checkedItems() if hasattr(self.rd_country1, 'checkedItems') else [self.rd_country1.currentText()]
            c_displays = [c for c in c_displays if c and not c.startswith('---')]
            if not c_displays:
                return
            try:
                y_start = int(self.rd_start.currentText()) if hasattr(self, 'rd_start') and self.rd_start.currentText() else 2000
            except (ValueError, AttributeError):
                y_start = 2000
            try:
                y_end = int(self.rd_end.currentText()) if hasattr(self, 'rd_end') and self.rd_end.currentText() else 2024
            except (ValueError, AttributeError):
                y_end = 2024
            if y_start > y_end:
                y_start, y_end = y_end, y_start
            y = y_end
            df_y = self.df[self.df['Yıl'] == y].copy()

            def _sg(row, col):
                try:
                    if row is None:
                        return np.nan
                    val = row[col] if col in row.index else np.nan
                    return float(val) if pd.notna(val) else np.nan
                except Exception:
                    return np.nan

            try:
                self.draw_welfare_chart()
            except Exception as _e:
                print(f"[draw_welfare_chart] hata: {_e}")
            try:
                self.draw_inequality_chart()
            except Exception as _e:
                print(f"[draw_inequality_chart] hata: {_e}")

            if hasattr(self, 'p3_narrative'):
                def _fv(row, c, dec=2):
                    v = _sg(row, c)
                    return f"{v:.{dec}f}" if pd.notna(v) else "N/A"
                def _clr(v):
                    if not pd.notna(v):
                        return '#7f8c8d'
                    return '#27ae60' if float(v) >= 0.7 else ('#e67e22' if float(v) >= 0.5 else '#c0392b')
                is_en = self.current_lang == 'en'
                rows_html = []
                for c_display in c_displays:
                    c = self._en_country(c_display)
                    if not c:
                        continue
                    r_c = df_y[df_y['Ülke'] == c].iloc[0] if not df_y[df_y['Ülke'] == c].empty else None
                    cd = self._display_country(c)
                    hdi_val = _sg(r_c, 'HDI_UNDP')
                    rows_html.append(
                        f"<b>{cd}:</b> HDI: <span style='color:{_clr(hdi_val)};'>{_fv(r_c,'HDI_UNDP',3)}</span> | "
                        f"IHDI: {_fv(r_c,'IHDI',3)} | Gini: {_fv(r_c,'Gini',1)} | GII: {_fv(r_c,'GII',3)}"
                    )
                per_lbl = 'Period' if is_en else 'Dönem'
                n_html = (
                    f"<div style=\"font-family:'Segoe UI',sans-serif;font-size:12px;color:#2c3e50;line-height:1.5;\">"
                    f"<b style='color:#1a5276;'>{'Development & Distribution Analysis' if is_en else 'Kalkınma & Bölüşüm Analizi'}</b>"
                    f" &nbsp;|&nbsp; {per_lbl}: {y_start}–{y_end}<br>"
                    f"{'<br>'.join(rows_html)}<br><div style='margin-top:8px;'>"
                    f"<div style='margin-bottom:2px;'>{self._get_formatted_source('HDI_UNDP')}</div>"
                    f"<div style='margin-bottom:2px;'>{self._get_formatted_source('GII')}</div>"
                    f"<div>{self._get_formatted_source('Gini')}</div>"
                    f"</div></div>"
                )
                self.p3_narrative.setHtml(n_html)
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"[update_risk] Genel hata: {e}")

    def draw_welfare_chart(self):
        """HDI, IHDI, PHDI, GDI ve PISA zaman serisi."""
        if self.df is None or not hasattr(self, 'rd_welfare_web'):
            return
        c_displays = self.rd_country1.checkedItems() if hasattr(self.rd_country1, 'checkedItems') else [self.rd_country1.currentText()]
        c_displays = [c for c in c_displays if c and not c.startswith('---')]
        if not c_displays:
            return
        try:
            y_start = int(self.rd_start.currentText())
        except Exception:
            y_start = 2000
        try:
            y_end = int(self.rd_end.currentText())
        except Exception:
            y_end = 2024
        if y_start > y_end:
            y_start, y_end = y_end, y_start
        is_en = self.current_lang == 'en'
        show_hdi  = getattr(self, 'act_hdi',  None) and self.act_hdi.isChecked()
        show_ihdi = getattr(self, 'act_ihdi', None) and self.act_ihdi.isChecked()
        show_phdi = getattr(self, 'act_phdi', None) and self.act_phdi.isChecked()
        show_gdi  = getattr(self, 'act_gdi',  None) and self.act_gdi.isChecked()
        show_pisa = getattr(self, 'act_pisa', None) and self.act_pisa.isChecked()
        pf = go.Figure()
        has_data = False
        palette = [
            ('HDI_UNDP', 'HDI',  '#2980b9', 'circle',      'solid',   show_hdi),
            ('IHDI',     'IHDI', '#27ae60', 'diamond',     'dot',     show_ihdi),
            ('PHDI',     'PHDI', '#8e44ad', 'square',      'dash',    show_phdi),
            ('GDI',      'GDI',  '#e67e22', 'triangle-up', 'dashdot', show_gdi),
        ]
        pisa_col = 'PISA' if 'PISA' in self.df.columns else None
        colors_c = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#16a085', '#34495e']
        for ci, c_lbl in enumerate(c_displays):
            c = self._en_country(c_lbl)
            if not c:
                continue
            df_c = self.df[(self.df['Ülke'] == c) & (self.df['Yıl'] >= y_start) & (self.df['Yıl'] <= y_end)].sort_values('Yıl')
            cn = self._display_country(c)
            base_clr = colors_c[ci % len(colors_c)]
            for col, lbl, clr, sym, dash, show in palette:
                if not show or col not in df_c.columns:
                    continue
                df_col = df_c.dropna(subset=[col])
                if df_col.empty:
                    continue
                r_int, g_int, b_int = int(base_clr[1:3], 16), int(base_clr[3:5], 16), int(base_clr[5:7], 16)
                alpha = 0.12 if ci == 0 else 0.0
                final_clr = colors_c[ci % len(colors_c)]
                pf.add_trace(go.Scatter(
                    x=df_col['Yıl'], y=df_col[col], mode='lines+markers',
                    name=f'{cn} — {lbl}',
                    line=dict(color=final_clr, width=2),
                    marker=dict(size=8, symbol=sym, color=final_clr),
                    fill='tozeroy' if (ci == 0 and col == 'HDI_UNDP' and show_hdi and len(c_displays) == 1) else 'none',
                    fillcolor=f'rgba({r_int},{g_int},{b_int},{alpha})'
                ))
                has_data = True
            if show_pisa and pisa_col:
                df_p = df_c.dropna(subset=[pisa_col])
                if not df_p.empty:
                    pf.add_trace(go.Bar(
                        x=df_p['Yıl'], y=df_p[pisa_col],
                        name=f'{cn} — PISA',
                        marker_color=f'rgba({int(base_clr[1:3],16)},{int(base_clr[3:5],16)},{int(base_clr[5:7],16)},0.5)',
                        yaxis='y2'
                    ))
                    has_data = True
        if not has_data:
            msg = 'No data found.' if is_en else 'Seçili ülkeler için veri bulunamadı.'
            pf.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False, font=dict(size=12, color='#95a5a6'))
        title_txt = 'Development & Welfare: HDI · IHDI · PHDI · GDI · PISA' if is_en else 'Kalkınma & Refah: HDI · IHDI · PHDI · GDI · PISA'
        layout = dict(
            title=dict(text=title_txt, font=dict(size=11, color='#1a5276')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1'),
            yaxis=dict(title='Index (0–1)', showgrid=True, gridcolor='#ecf0f1', range=[0, 1.05]),
            yaxis2=dict(title='PISA Score', overlaying='y', side='right', showgrid=False) if pisa_col else {},
            paper_bgcolor='#fafafa', plot_bgcolor='#f7f9fb',
            margin=dict(l=45, r=45, t=40, b=40),
            hovermode='x unified', hoverlabel=dict(font_size=13),
            legend=dict(orientation='h', y=-0.22, font=dict(size=8))
        )
        pf.update_layout(**layout)
        _load_plotly_to_view(self.rd_welfare_web, pf)

    def draw_inequality_chart(self):
        if self.df is None or not hasattr(self, 'rd_ineq_web'):
            return
        c_displays = self.rd_country1.checkedItems() if hasattr(self.rd_country1, 'checkedItems') else [self.rd_country1.currentText()]
        c_displays = [c for c in c_displays if c and not c.startswith('---')]
        if not c_displays:
            return
        try:
            y_start = int(self.rd_start.currentText())
        except Exception:
            y_start = 2000
        try:
            y_end = int(self.rd_end.currentText())
        except Exception:
            y_end = 2024
        if y_start > y_end:
            y_start, y_end = y_end, y_start
        is_en = getattr(self, 'current_lang', 'tr') == 'en'
        show_gini  = getattr(self, 'act_gini',  None) and self.act_gini.isChecked()
        show_owid_gini = getattr(self, 'act_owid_gini', None) and self.act_owid_gini.isChecked()
        show_gii   = getattr(self, 'act_gii',   None) and self.act_gii.isChecked()
        show_palma = getattr(self, 'act_palma', None) and self.act_palma.isChecked()
        show_wiid  = getattr(self, 'act_wiid',  None) and self.act_wiid.isChecked()
        show_pov   = getattr(self, 'act_pov',   None) and self.act_pov.isChecked()
        pf = go.Figure()
        has_data = False
        palette = [
            ('Gini',        'Gini (WB)',   '#c0392b', 'circle',      'solid',   show_gini),
            ('OWID Gini',   'Gini (OWID)', '#e74c3c', 'x',           'solid',   show_owid_gini),
            ('GII',         'GII',         '#8e44ad', 'diamond',     'dot',     show_gii),
            ('Mutlak Yoksulluk (%)', 'Mutlak Yoksulluk', '#f39c12', 'square', 'solid', show_pov),
            ('palma_ratio', 'Palma Ratio', '#d35400', 'triangle-up', 'dash',    show_palma),
            ('WIID_Ratio',  'WIID S10/S1', '#2980b9', 'star',        'dashdot', show_wiid),
        ]
        colors_c = ['#c0392b', '#2980b9', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#16a085', '#34495e']
        for ci, c_lbl in enumerate(c_displays):
            c = self._en_country(c_lbl)
            if not c:
                continue
            df_c = self.df[(self.df['Ülke'] == c) & (self.df['Yıl'] >= y_start) & (self.df['Yıl'] <= y_end)].sort_values('Yıl')
            cn = self._display_country(c)
            base_clr = colors_c[ci % len(colors_c)]
            for col, lbl, clr, sym, dash, show in palette:
                if not show or col not in df_c.columns:
                    continue
                df_col = df_c.dropna(subset=[col])
                if df_col.empty:
                    continue
                final_clr = base_clr
                if col == 'Gini':
                    pf.add_trace(go.Bar(
                        x=df_col['Yıl'], y=df_col[col],
                        name=f'{cn} — {lbl}',
                        marker_color=f'rgba({int(final_clr[1:3],16)},{int(final_clr[3:5],16)},{int(final_clr[5:7],16)},0.5)',
                        yaxis='y1'
                    ))
                else:
                    pf.add_trace(go.Scatter(
                        x=df_col['Yıl'], y=df_col[col], mode='lines+markers',
                        name=f'{cn} — {lbl}',
                        line=dict(color=final_clr, width=2),
                        marker=dict(size=8, symbol=sym, color=final_clr),
                        yaxis='y2' if col in ('palma_ratio', 'WIID_Ratio') else 'y1'
                    ))
                has_data = True
        if not has_data:
            msg = 'No data found.' if is_en else 'Seçili ülkeler için veri bulunamadı.'
            pf.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False, font=dict(size=12, color='#95a5a6'))
        title_txt = 'Inequality Metrics: Gini · GII · Palma' if is_en else 'Eşitsizlik Metrikleri: Gini · GII · Palma Ratio'
        layout = dict(
            title=dict(text=title_txt, font=dict(size=11, color='#c0392b')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1'),
            yaxis=dict(title='Index (Gini/GII)', showgrid=True, gridcolor='#ecf0f1'),
            yaxis2=dict(title='Ratio (Palma / WIID)', overlaying='y', side='right', showgrid=False) if (show_palma or show_wiid) else {},
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=45, r=45, t=40, b=40),
            hovermode='x unified', hoverlabel=dict(font_size=13),
            legend=dict(orientation='h', y=-0.22, font=dict(size=8))
        )
        pf.update_layout(**layout)
        _load_plotly_to_view(self.rd_ineq_web, pf)
        self._rd_ineq_fig = pf

    def export_risk_pdf(self):
        fn, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "Risk_Analiz_Raporu.pdf", "PDF (*.pdf)")
        if fn:
            try:
                pf = getattr(self, '_rd_ineq_fig', None)
                if not pf:
                    QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak grafik bulunamadı.")
                    return
                pf.write_image(fn, format="pdf")
                QMessageBox.information(self, "Başarılı", "Risk Analizi Raporu Kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {e}")
