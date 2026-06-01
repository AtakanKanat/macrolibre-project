"""
page_macro.py — Mixin: Makroekonomi (Page 1)
plot_macro, toggle_macro_mode, update_macro_ui
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sbf_terminal.utils import _load_plotly_to_view, get_econ_fmt


class MacroMixin:
    """Page 1 — Makroekonomi grafikleri."""

    def toggle_macro_mode(self):
        self.macro_mode = "instant" if self.btn_macro_mode.isChecked() else "period"
        self.btn_macro_mode.setText(self.t('mode_period') if self.macro_mode == "instant" else self.t('mode_instant'))
        self.lbl_macro_dash.setVisible(self.macro_mode == "period")
        self.macro_end.setVisible(self.macro_mode == "period")
        self.lbl_macro_per.setText(self.t('year') + ":" if self.macro_mode == "instant" else self.t('period_lbl'))
        self.plot_macro()

    def update_macro_ui(self):
        price_inds = ["GSYİH", "GSMH", "Kişi Başı GSYİH", "Kişi Başı GSMH",
                      "GDP", "GNI", "GDP Per Capita", "GNI Per Capita"]
        checked = self.macro_cmb.checkedItems() if hasattr(self.macro_cmb, 'checkedItems') else [self.macro_cmb.currentText()]
        any_price_supported = any(i in price_inds for i in checked)
        self.macro_price.setEnabled(bool(any_price_supported))

    def plot_macro(self):
        if self.df is None:
            return
        self.update_macro_ui()
        ind_displays = self.macro_cmb.checkedItems() if hasattr(self.macro_cmb, 'checkedItems') else [self.macro_cmb.currentText()]
        ind_displays = [i for i in ind_displays if i and not i.startswith('---')]
        if not ind_displays:
            return

        c_displays = self.macro_c.checkedItems() if hasattr(self.macro_c, 'checkedItems') else [self.macro_c.currentText()]
        c_displays = [c for c in c_displays if c and not c.startswith('---')]
        if not c_displays:
            return

        if not hasattr(self, 'macro_start') or not self.macro_start.currentText() or not self.macro_end.currentText():
            return
        y1 = int(self.macro_start.currentText())
        y2 = int(self.macro_end.currentText())

        price_type_val = self.macro_price.currentText() if self.macro_price.isEnabled() else 'Nominal'
        base_year_str = '2015'
        base_year = 2015

        df_real = self.df.copy()
        if 'region' in df_real.columns:
            df_real = df_real[df_real['region'].notna() & (df_real['region'] != '')]

        years = list(range(y1, y2 + 1))
        pf = go.Figure()
        colors_master = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad',
                         '#e67e22', '#16a085', '#34495e', '#d35400', '#2c3e50']
        trace_colors = colors_master
        has_data = False

        if self.macro_mode == "instant":
            for idx_i, ind_display in enumerate(ind_displays):
                ind = self._resolve_ind(ind_display)
                x_vals, y_vals, marker_colors = [], [], []
                for idx_c, c_display in enumerate(c_displays):
                    is_global = c_display.startswith('🌍')
                    c_iso = self._en_country(c_display) if not is_global else None
                    actual_ind = ind
                    df_y = df_real[df_real['Yıl'] == y1].copy()
                    if not is_global:
                        df_y = df_y[df_y['Ülke'] == c_iso]
                    if df_y.empty:
                        continue
                    if price_type_val in ['Reel', 'Real'] and self.macro_price.isEnabled():
                        if ind == 'GSYİH':
                            actual_ind = 'GSYİH (Reel)'
                        elif ind in ['GSMH', 'Kişi Başı GSYİH', 'Kişi Başı GSMH']:
                            actual_ind = f'{ind} (Reel)'
                            if 'GSYİH (Reel)' in df_y.columns and 'GSYİH' in df_y.columns and ind in df_y.columns:
                                deflator = df_y['GSYİH (Reel)'] / df_y['GSYİH']
                                df_y[actual_ind] = df_y[ind] * deflator
                    if actual_ind not in df_y.columns:
                        continue
                    df_y = df_y.dropna(subset=[actual_ind])
                    if df_y.empty:
                        continue
                    val = np.nan
                    if is_global:
                        if ind in ['GSYİH', 'GSMH', 'GSYİH (Reel)', 'GSMH (Reel)']:
                            val = df_y[actual_ind].sum()
                        else:
                            val = df_y[actual_ind].mean()
                    else:
                        val = df_y[actual_ind].values[0]
                    if pd.notna(val):
                        disp_name = c_display
                        if is_global:
                            disp_name = ('Global Total' if ind in ['GSYİH', 'GSMH'] else 'Global Average') if self.current_lang == 'en' else ('Küresel Toplam' if ind in ['GSYİH', 'GSMH'] else 'Küresel Ortalama')
                        x_vals.append(disp_name)
                        y_vals.append(val)
                        marker_colors.append(trace_colors[idx_c % len(trace_colors)] if len(ind_displays) == 1 else trace_colors[idx_i % len(trace_colors)])
                        has_data = True
                if x_vals:
                    ind_name = self.t('ind_names').get(ind_display, ind_display)
                    pf.add_trace(go.Bar(
                        x=x_vals, y=y_vals, name=ind_name,
                        marker_color=marker_colors if len(ind_displays) == 1 else trace_colors[idx_i % len(trace_colors)],
                        text=[get_econ_fmt(self.current_lang)(v) for v in y_vals],
                        textposition='auto'
                    ))
            pf.update_layout(barmode='group')
        else:
            for idx_i, ind_display in enumerate(ind_displays):
                ind = self._resolve_ind(ind_display)
                for idx_c, c_display in enumerate(c_displays):
                    agg_values, valid_years = [], []
                    is_global = c_display.startswith('🌍')
                    c_iso = self._en_country(c_display) if not is_global else None
                    actual_ind = ind
                    for y in years:
                        df_y = df_real[df_real['Yıl'] == y].copy() if is_global else df_real[(df_real['Ülke'] == c_iso) & (df_real['Yıl'] == y)].copy()
                        if df_y.empty:
                            continue
                        if price_type_val in ['Reel', 'Real'] and self.macro_price.isEnabled():
                            if ind == 'GSYİH':
                                actual_ind = 'GSYİH (Reel)'
                            elif ind in ['GSMH', 'Kişi Başı GSYİH', 'Kişi Başı GSMH']:
                                actual_ind = f'{ind} (Reel)'
                                if 'GSYİH (Reel)' in df_y.columns and 'GSYİH' in df_y.columns and ind in df_y.columns:
                                    deflator = df_y['GSYİH (Reel)'] / df_y['GSYİH']
                                    df_y[actual_ind] = df_y[ind] * deflator
                        if actual_ind not in df_y.columns:
                            continue
                        df_y = df_y.dropna(subset=[actual_ind])
                        if df_y.empty:
                            continue
                        val = df_y[actual_ind].sum() if is_global and ind in ['GSYİH', 'GSMH', 'GSYİH (Reel)', 'GSMH (Reel)'] else (df_y[actual_ind].mean() if is_global else df_y[actual_ind].values[0])
                        if pd.notna(val):
                            agg_values.append(val)
                            valid_years.append(y)
                    if valid_years:
                        has_data = True
                        trace_name = c_display
                        if is_global:
                            trace_name = ('Global Total' if ind in ['GSYİH', 'GSMH'] else 'Global Average') if self.current_lang == 'en' else ('Küresel Toplam' if ind in ['GSYİH', 'GSMH'] else 'Küresel Ortalama')
                        if len(ind_displays) > 1:
                            trace_name = f"{trace_name} - {ind_display}"
                        color = trace_colors[idx_c % len(trace_colors)]
                        symbols = ['circle', 'square', 'diamond', 'triangle-up', 'cross', 'x', 'pentagon', 'star']
                        symbol = symbols[idx_i % len(symbols)]
                        pf.add_trace(go.Scatter(
                            x=valid_years, y=agg_values, mode='lines+markers',
                            name=trace_name,
                            line=dict(color=color, width=3),
                            marker=dict(size=8, symbol=symbol),
                            fill='tozeroy' if (len(c_displays) == 1 and len(ind_displays) == 1) else 'none',
                            fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)'
                        ))

        if not has_data:
            self.macro_web.setHtml("<h3 style='text-align:center; color:#e74c3c; margin-top:50px;'>Yeterli veri bulunamadı.</h3>")
            return

        is_en = self.current_lang == 'en'
        if len(ind_displays) == 1:
            ind_disp = self.t('ind_names').get(ind_displays[0], ind_displays[0])
            if price_type_val in ['Reel', 'Real'] and self.macro_price.isEnabled():
                reel_lbl = 'Real' if is_en else 'Reel'
                ind_disp = f'{ind_disp} ({reel_lbl}, {base_year})'
            chart_title = f'Macroeconomic Profile: {ind_disp} ({y1}–{y2})' if is_en else f'Makroekonomik Profil: {ind_disp} ({y1}–{y2})'
            y_title = ind_disp
        else:
            ind_disp = "Karşılaştırmalı Göstergeler" if not is_en else "Comparative Indicators"
            chart_title = f'Macroeconomic Profile: {ind_disp} ({y1}–{y2})' if is_en else f'Makroekonomik Profil: {ind_disp} ({y1}–{y2})'
            y_title = "Değer" if not is_en else "Value"

        pf.update_layout(
            title=dict(text=chart_title, font=dict(size=14, color='#2c3e50')),
            xaxis=dict(title='Years' if is_en else 'Yıllar', showgrid=True, gridcolor='#ecf0f1',
                       dtick=2 if self.macro_mode == "period" else None),
            yaxis=dict(title=y_title, showgrid=True, gridcolor='#ecf0f1'),
            barmode='group',
            paper_bgcolor='#fafafa', plot_bgcolor='#f7f9fb',
            margin=dict(l=50, r=20, t=60, b=80),
            hovermode='x unified',
            hoverlabel=dict(font_size=13),
            legend=dict(orientation='h', yanchor='top', y=-0.12, xanchor='center', x=0.5, font=dict(size=10))
        )
        _load_plotly_to_view(self.macro_web, pf)
        self._macro_fig = pf

        if hasattr(self, 'p1_narrative') and hasattr(self, 'indicator_metadata'):
            srcs = []
            for idx_i, ind_display in enumerate(ind_displays):
                ind = self._resolve_ind(ind_display)
                actual_ind = ind
                if price_type_val in ['Reel', 'Real'] and self.macro_price.isEnabled():
                    if ind == 'GSYİH':
                        actual_ind = 'GSYİH (Reel)'
                    elif ind in ['GSMH', 'Kişi Başı GSYİH', 'Kişi Başı GSMH']:
                        actual_ind = f'{ind} (Reel)'
                meta_key = actual_ind if actual_ind in self.indicator_metadata else ind
                # Tek ülke seçiliyse ISO'yu al (kaynak override için)
                selected_iso = None
                if len(c_displays) == 1 and not c_displays[0].startswith('🌍'):
                    c_en = self._en_country(c_displays[0])
                    iso_row = self.df[self.df['Ülke'] == c_en]['ISO']
                    if not iso_row.empty:
                        selected_iso = iso_row.iloc[0]
                meta = self._get_metadata(meta_key, iso=selected_iso)
                if not meta:
                    continue
                ind_name_tr = self.t('ind_names').get(ind_display, ind_display)
                name = ind_name_tr
                if actual_ind.endswith('(Reel)'):
                    reel_lbl = 'Real' if self.current_lang == 'en' else 'Reel'
                    name = f"{ind_name_tr} ({reel_lbl}, {base_year_str})"
                colors_alt = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#16a085', '#34495e']
                color = colors_alt[idx_i % len(colors_alt)]
                srcs.append(f"<li style='margin-bottom:8px;'><span style='color:{color}; font-weight:bold;'>■ {name}</span><br>{meta[2]}</li>")
            is_en = self.current_lang == 'en'
            lbl_src = 'Data Sources' if is_en else 'Veri Kaynağı'
            n_html = f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:12px; color:#2c3e50; line-height:1.5;">
                <div style="margin-bottom:8px;">
                    <b style="color:#1a5276;">📚 {lbl_src}</b>
                    <ul style="list-style-type:none; padding-left:5px; margin-top:5px;">
                        {''.join(srcs)}
                    </ul>
                </div>
            """
            if len(c_displays) > 1:
                msg = f'{len(c_displays)} countries selected.' if is_en else f'{len(c_displays)} ülke seçildi.'
                n_html += f"<div style='padding-top:5px; font-size:12px;'><i>{msg}</i></div>"
            n_html += "</div>"
            self.p1_narrative.setHtml(n_html)

    def export_macro_pdf(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        fn, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "Makroekonomi_Raporu.pdf", "PDF (*.pdf)")
        if fn:
            try:
                pf = getattr(self, '_macro_fig', None)
                if not pf:
                    QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak grafik bulunamadı.")
                    return
                pf.write_image(fn, format="pdf")
                QMessageBox.information(self, "Başarılı", "Makroekonomi Raporu Kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {e}")

