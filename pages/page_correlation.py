"""
page_correlation.py — Mixin: Korelasyon Analizi (Page 9)
draw_corr_chart, toggle_corr_mode
"""
import numpy as np
import plotly.graph_objects as go

from sbf_terminal.utils import _load_plotly_to_view


class CorrelationMixin:
    """Page 9 — Korelasyon Analizi."""

    def toggle_corr_mode(self):
        self.corr_mode = "instant" if self.btn_corr_mode.isChecked() else "period"
        self.btn_corr_mode.setText(self.t('mode_period') if self.corr_mode == "instant" else self.t('mode_instant'))
        self.lbl_corr_per.setVisible(self.corr_mode == "period")
        self.corr_start.setVisible(self.corr_mode == "period")
        self.corr_end.setVisible(self.corr_mode == "period")
        self.lbl_corr_year.setVisible(self.corr_mode == "instant")
        self.corr_year.setVisible(self.corr_mode == "instant")
        self.draw_corr_chart()

    def draw_corr_chart(self):
        if self.df is None:
            return
        try:
            x_disp = self.corr_x.currentText()
            y_disp = self.corr_y.currentText()
            if not x_disp or not y_disp:
                return
            x_ind = self._resolve_ind(x_disp)
            y_ind = self._resolve_ind(y_disp)
            c_displays = self.corr_c.checkedItems()
            if not c_displays:
                txt = self.corr_c.currentText()
                c_displays = [txt] if txt and not txt.startswith("---") else []
            if not c_displays:
                self.corr_web.setHtml("<body><h3 style='color:gray; text-align:center;'>Lütfen en az bir ülke seçiniz.</h3></body>")
                return
            is_en = self.current_lang == 'en'
            all_lbl = "🌍 All (All Countries)" if is_en else "🌍 Hepsi (Tüm Ülkeler)"
            is_all = all_lbl in c_displays
            if self.corr_mode == "instant":
                try:
                    ty = int(self.corr_year.currentText())
                except Exception:
                    ty = 2024
                sy, ey = ty, ty
            else:
                s_year, e_year = self.corr_start.currentText(), self.corr_end.currentText()
                try:
                    sy, ey = int(s_year), int(e_year)
                except Exception:
                    sy, ey = 2000, 2024
            if is_all:
                cdf = self.df[(self.df['Yıl'] >= sy) & (self.df['Yıl'] <= ey)].copy()
                if 'aggregate' in cdf.columns:
                    cdf = cdf[cdf['aggregate'] == False]
            else:
                c_en_list = [self._en_country(cd) for cd in c_displays]
                cdf = self.df[(self.df['Ülke'].isin(c_en_list)) & (self.df['Yıl'] >= sy) & (self.df['Yıl'] <= ey)].copy()
            cdf = cdf.dropna(subset=[x_ind, y_ind])
            if cdf.empty:
                self.corr_web.setHtml(f"<body><h3 style='color:gray; text-align:center;'>{self.t('desc_no_data')}</h3></body>")
                return
            cdf = cdf.sort_values(['Yıl', 'Ülke'])
            corr_val = cdf[x_ind].corr(cdf[y_ind])
            fig = go.Figure()
            show_trend = self.chk_corr_trend.isChecked()
            show_regions = self.chk_corr_color.isChecked()
            if show_regions:
                def map_continent(reg_str):
                    if not isinstance(reg_str, str): return 'Other' if is_en else 'Diğer'
                    r = reg_str.upper()
                    if r == 'ECS': return 'Europe' if is_en else 'Avrupa'
                    if r in ['LCN', 'NAC']: return 'Americas' if is_en else 'Amerika'
                    if r in ['EAS', 'SAS']: return 'Asia & Oceania' if is_en else 'Asya ve Okyanusya'
                    if r in ['MEA', 'SSF']: return 'Africa & Middle East' if is_en else 'Afrika ve Ortadoğu'
                    return 'Other' if is_en else 'Diğer'
                
                cdf['continent'] = cdf['region'].apply(map_continent)
                regions = cdf['continent'].unique()
                for reg in regions:
                    reg_df = cdf[cdf['continent'] == reg]
                    fig.add_trace(go.Scatter(
                        x=reg_df[x_ind], y=reg_df[y_ind], mode='markers',
                        marker=dict(size=12 if self.corr_mode == "instant" else 10, opacity=0.8, line=dict(width=1, color='white')),
                        text=[f"{self._display_country(row['Ülke'])} ({row['Yıl']})" for _, row in reg_df.iterrows()],
                        hoverinfo='text+x+y',
                        name=str(reg)
                    ))
            else:
                fig.add_trace(go.Scatter(
                    x=cdf[x_ind], y=cdf[y_ind], mode='markers',
                    marker=dict(size=12 if self.corr_mode == "instant" else 10, color='#2980b9', opacity=0.7, line=dict(width=1, color='white')),
                    text=[f"{self._display_country(row['Ülke'])} ({row['Yıl']})" for _, row in cdf.iterrows()],
                    hoverinfo='text+x+y',
                    name='Veri Noktaları' if not is_en else 'Data Points'
                ))
            if show_trend and len(cdf) > 1:
                try:
                    z = np.polyfit(cdf[x_ind], cdf[y_ind], 1)
                    p = np.poly1d(z)
                    x_range = np.linspace(cdf[x_ind].min(), cdf[x_ind].max(), 100)
                    fig.add_trace(go.Scatter(
                        x=x_range, y=p(x_range), mode='lines',
                        line=dict(color='#e74c3c', width=2, dash='dash'),
                        name='Trend Hattı' if not is_en else 'Trend Line'
                    ))
                except Exception:
                    pass
            title_prefix = f"{sy}" if self.corr_mode == "instant" else f"{sy}-{ey}"
            title_txt = f"{title_prefix} | {x_disp} vs {y_disp} {'Correlation' if is_en else 'Korelasyonu'}"
            if is_all:
                title_txt += f" ({'All Countries' if is_en else 'Tüm Ülkeler'})"
            fig.update_layout(
                title=dict(text=f"<b>{title_txt}</b>", font=dict(size=14, color='#1a5276')),
                xaxis=dict(title=x_disp, showgrid=True, gridcolor='#ecf0f1'),
                yaxis=dict(title=y_disp, showgrid=True, gridcolor='#ecf0f1'),
                paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
                margin=dict(l=60, r=40, t=60, b=60),
                hovermode='closest',
                template='plotly_white' if self.current_theme == 'light' else 'plotly_dark',
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            fig.add_annotation(
                text=f"Pearson R: {corr_val:.3f}",
                xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False,
                font=dict(size=14, color="#c0392b", family="Courier New, monospace"),
                bgcolor="rgba(255,255,255,0.8)", bordercolor="#c0392b", borderwidth=1
            )
            _load_plotly_to_view(self.corr_web, fig)
            srcs = ""
            if hasattr(self, 'indicator_metadata'):
                lbl_src = 'Data Sources' if is_en else 'Veri Kaynağı'
                meta_x = self._get_metadata(x_ind)
                meta_y = self._get_metadata(y_ind)
                if meta_x:
                    srcs += f"<li style='margin-bottom:4px;'><span style='color:#2980b9; font-weight:bold;'>■ {x_disp}</span>: {meta_x[2]}</li>"
                if meta_y:
                    srcs += f"<li style='margin-bottom:4px;'><span style='color:#e74c3c; font-weight:bold;'>■ {y_disp}</span>: {meta_y[2]}</li>"
                if srcs:
                    srcs = f"<div style='font-size:12px;'><b style='color:#1a5276;'>📚 {lbl_src}</b><ul style='list-style-type:none; padding-left:5px; margin-top:5px;'>{srcs}</ul></div>"

            self.corr_narrative.setHtml(f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:13px; color:#2c3e50; line-height:1.6;">
                {srcs}
                <hr style='border:0; border-top:1px solid #eee; margin:10px 0;'>
                <span style='color:#7f8c8d; font-size:11px;'><i>{'Note: Correlation does not imply causality.' if is_en else 'Not: Korelasyon nedensellik anlamına gelmez.'} ({len(cdf)} {'observations' if is_en else 'gözlem'})</i></span>
            </div>""")
        except Exception as e:
            import traceback; traceback.print_exc()
