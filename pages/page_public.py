"""
page_public.py — Mixin: Kamu Maliyesi (Page 6)
draw_pub_chart, toggle_pub_mode
"""
import pandas as pd
import plotly.graph_objects as go

from sbf_terminal.utils import _load_plotly_to_view


class PublicMixin:
    """Page 6 — Kamu Maliyesi."""

    def toggle_pub_mode(self):
        self.pub_mode = "instant" if self.btn_pub_mode.isChecked() else "period"
        self.btn_pub_mode.setText(self.t('mode_period') if self.pub_mode == "instant" else self.t('mode_instant'))
        self.lbl_pub_dash.setVisible(self.pub_mode == "period")
        self.pub_end.setVisible(self.pub_mode == "period")
        self.lbl_pub_per.setText(self.t('year') + ":" if self.pub_mode == "instant" else self.t('period_lbl'))
        self.draw_pub_chart()

    def draw_pub_chart(self):
        if self.df is None:
            return
        c_displays = self.pub_c.checkedItems() if hasattr(self.pub_c, 'checkedItems') else [self.pub_c.currentText()]
        c_displays = [c for c in c_displays if c and not c.startswith('---')]
        if not c_displays:
            return
        try:
            y1 = int(self.pub_start.currentText())
            y2 = int(self.pub_end.currentText())
        except Exception:
            return
        pf = go.Figure()
        mapping = {
            "Kamu Harcamaları": ("Kamu Harcamaları", "#3498db"),
            "Eğitim Harcamaları": ("Eğitim", "#f1c40f"),
            "Sağlık Harcamaları": ("Sağlık", "#e74c3c"),
            "Savunma Harcamaları": ("Savunma Harcamaları", "#9b59b6"),
            "Vergi Gelirleri": ("Vergi Gelirleri", "#1abc9c"),
            "Bütçe Dengesi": ("Bütçe Dengesi", "#34495e"),
            "Dış Borç": ("Dış Borç", "#e67e22"),
            "Cari Denge": ("Cari Denge", "#7f8c8d"),
            "Gov Expenditure": ("Kamu Harcamaları", "#3498db"),
            "Education Exp.": ("Eğitim", "#f1c40f"),
            "Health Exp.": ("Sağlık", "#e74c3c"),
            "Military Exp.": ("Savunma Harcamaları", "#9b59b6"),
            "Tax Revenue": ("Vergi Gelirleri", "#1abc9c"),
            "Budget Balance": ("Bütçe Dengesi", "#34495e"),
            "External Debt": ("Dış Borç", "#e67e22"),
            "Current Account": ("Cari Denge", "#7f8c8d")
        }
        active_inds_disp = self.pub_ind.checkedItems()
        inds = [(True, mapping[d][0], mapping[d][1]) for d in active_inds_disp if d in mapping]
        has_data = False
        is_en = getattr(self, 'current_lang', 'tr') == 'en'
        base_colors = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad',
                       '#e67e22', '#16a085', '#34495e', '#d35400', '#2c3e50']
        if self.pub_mode == "instant":
            for is_checked, ind, color in inds:
                if not is_checked:
                    continue
                ind_name = self.t('ind_names').get(ind, ind)
                x_vals, y_vals = [], []
                for c_display in c_displays:
                    c = self._en_country(c_display)
                    if not c:
                        continue
                    d = self.df[(self.df['Ülke'] == c) & (self.df['Yıl'] == y1)].copy()
                    if d.empty or ind not in d.columns:
                        continue
                    val = d[ind].values[0]
                    if pd.notna(val):
                        x_vals.append(c_display)
                        y_vals.append(val)
                        has_data = True
                if x_vals:
                    pf.add_trace(go.Bar(
                        x=x_vals, y=y_vals, name=ind_name, marker_color=color,
                        text=[f"%{v:.1f}" for v in y_vals], textposition='auto'
                    ))
            pf.update_layout(barmode='group')
        else:
            for idx, c_display in enumerate(c_displays):
                c = self._en_country(c_display)
                if not c:
                    continue
                d = self.df[(self.df['Ülke'] == c) & (self.df['Yıl'] >= y1) & (self.df['Yıl'] <= y2)].sort_values('Yıl').copy()
                if d.empty:
                    continue
                for i_idx, (is_checked, ind, color) in enumerate(inds):
                    if is_checked and ind in d.columns:
                        actual_d = d[['Yıl', ind]].dropna()
                        if not actual_d.empty:
                            has_data = True
                            ind_name = self.t('ind_names').get(ind, ind)
                            final_color = base_colors[idx % len(base_colors)]
                            symbols = ['circle', 'square', 'diamond', 'triangle-up', 'cross', 'x', 'pentagon', 'star']
                            symbol = symbols[i_idx % len(symbols)]
                            trace_name = f'{c_display} — {ind_name}' if len(c_displays) > 1 else ind_name
                            pf.add_trace(go.Scatter(
                                x=actual_d['Yıl'], y=actual_d[ind],
                                mode='lines+markers', name=trace_name,
                                line=dict(color=final_color, width=2),
                                marker=dict(size=8, color=final_color, symbol=symbol)
                            ))
        if not has_data:
            msg = 'No public finance data found.' if is_en else 'Kamu maliyesi verisi bulunamadı.'
            pf.add_annotation(text=msg, xref='paper', yref='paper', x=0.5, y=0.5, showarrow=False, font=dict(size=12, color='#95a5a6'))
        title_prefix = f"({y1})" if self.pub_mode == "instant" else f"({y1}-{y2})"
        title_txt = f"Public Finance & Expenditures {title_prefix}" if is_en else f"Kamu Maliyesi ve Harcamaları {title_prefix}"
        pf.update_layout(
            title=dict(text=title_txt, font=dict(size=13, color='#1a5276')),
            xaxis=dict(title='Year' if is_en else 'Yıl', showgrid=True, gridcolor='#ecf0f1',
                       dtick=2 if self.pub_mode == "period" else None),
            yaxis=dict(title='% GDP' if is_en else '% GSYİH', showgrid=True, gridcolor='#ecf0f1'),
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=45, r=20, t=40, b=80),
            hovermode='x unified', hoverlabel=dict(font_size=13),
            legend=dict(orientation='h', yanchor='top', y=-0.12, xanchor='center', x=0.5, font=dict(size=10))
        )
        _load_plotly_to_view(self.pub_web, pf)
        self._pub_fig = pf
        if hasattr(self, 'pub_narrative'):
            rows = []
            for is_checked, ind, color in inds:
                if is_checked:
                    meta = self._get_metadata(ind)
                    ind_name = self.t('ind_names').get(ind, ind)
                    rows.append(f"<li style='margin-bottom:8px;'><span style='color:{color}; font-weight:bold;'>■ {ind_name}</span><br>{meta[2]}</li>")
            c_msg = f"{len(c_displays)} countries selected." if is_en else f"{len(c_displays)} ülke seçildi."
            note = "Data Sources" if is_en else "Veri Kaynağı"
            rows_html = "".join(rows) if rows else f"<li>{'No active indicators.' if is_en else 'Aktif gösterge seçilmedi.'}</li>"
            self.pub_narrative.setHtml(f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:12px; color:#2c3e50; line-height:1.5;">
                <div style="margin-bottom:8px;">
                    <b style="color:#1a5276;">📚 {note}</b>
                    <ul style="list-style-type:none; padding-left:5px; margin-top:5px;">{rows_html}</ul>
                </div>
                <div style="padding-top:5px;"><i>{c_msg if len(c_displays)>1 else ''}</i></div>
            </div>""")

    def export_pub_pdf(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        fn, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "Kamu_Maliyesi_Raporu.pdf", "PDF (*.pdf)")
        if fn:
            try:
                pf = getattr(self, '_pub_fig', None)
                if not pf:
                    QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak grafik bulunamadı.")
                    return
                pf.write_image(fn, format="pdf")
                QMessageBox.information(self, "Başarılı", "Kamu Maliyesi Raporu Kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {e}")

