"""
page_risk.py — Mixin: Risk Analizi (Page 8)
draw_risk_chart
"""
import plotly.graph_objects as go
from sbf_terminal.utils import _load_plotly_to_view


class RiskMixin:
    """Page 8 — Risk Analizi."""

    def draw_risk_chart(self):
        if self.df is None:
            return
        try:
            c_displays = self.risk_c.checkedItems()
            if not c_displays:
                txt = self.risk_c.currentText()
                c_displays = [txt] if txt and not txt.startswith("---") else []
            if not c_displays:
                self.risk_web.setHtml("<body><h3 style='color:gray; text-align:center;'>Lütfen en az bir ülke seçiniz.</h3></body>")
                return
            s_year, e_year = self.risk_start.currentText(), self.risk_end.currentText()
            try:
                sy, ey = int(s_year), int(e_year)
            except Exception:
                sy, ey = 2000, 2024
            mapping = {
                "Cari İşlemler Dengesi": "Cari Açık", "Toplam Dış Borç Stoku": "Dış Borç-GNI",
                "Ülke Risk Primi (Proxy)": "Risk Primi", "İthalat Karşılama Süresi": "İthalat Karşılama",
                "Kısa Vadeli Borç / Rezerv": "Kısa Vadeli Borç", "DYY Girişi": "DYY-Girişi",
                "Reel Efektif Kur (REK)": "REK", "Reel Faiz Oranı": "Reel Faiz",
                "Bütçe Dengesi": "Bütçe Dengesi", "Borç Servisi": "Borç Servisi",
                "Current Account Balance": "Cari Açık", "External Debt Stock": "Dış Borç-GNI",
                "Risk Premium (Proxy)": "Risk Primi", "Import Cover (Months)": "İthalat Karşılama",
                "ST Debt / Reserves": "Kısa Vadeli Borç", "FDI Inflow": "DYY-Girişi",
                "REER Index": "REK", "Real Interest Rate": "Reel Faiz",
                "Budget Balance": "Bütçe Dengesi", "Debt Service": "Borç Servisi"
            }
            active_inds_disp = self.risk_ind.checkedItems()
            active_inds = [mapping.get(d, d) for d in active_inds_disp]
            if not active_inds:
                self.risk_web.setHtml("<body><h3 style='color:red; text-align:center;'>Lütfen en az bir gösterge seçiniz.</h3></body>")
                return
            fig = go.Figure()
            colors_list = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad',
                           '#e67e22', '#16a085', '#34495e', '#d35400', '#2c3e50']
            ind_names = self.t('ind_names') if isinstance(self.t('ind_names'), dict) else {}
            has_data = False
            for idx, c_disp in enumerate(c_displays):
                c_en = self._en_country(c_disp)
                cdf = self.df[(self.df['Ülke'] == c_en) & (self.df['Yıl'] >= sy) & (self.df['Yıl'] <= ey)].sort_values('Yıl')
                if cdf.empty:
                    continue
                for i_idx, ind in enumerate(active_inds):
                    if ind in cdf.columns:
                        temp = cdf.dropna(subset=[ind])
                        if not temp.empty:
                            has_data = True
                            color = colors_list[idx % len(colors_list)]
                            symbols = ['circle', 'square', 'diamond', 'triangle-up', 'cross', 'x', 'pentagon', 'star']
                            symbol = symbols[i_idx % len(symbols)]
                            trace_name = ind_names.get(ind, ind)
                            if len(c_displays) > 1:
                                trace_name = f"{c_disp} - {trace_name}"
                            fig.add_trace(go.Scatter(
                                x=temp['Yıl'], y=temp[ind],
                                name=trace_name, mode='lines+markers',
                                line=dict(width=2, color=color),
                                marker=dict(size=8, color=color, symbol=symbol)
                            ))
            if not has_data:
                self.risk_web.setHtml(f"<body><h3 style='color:gray; text-align:center;'>{self.t('desc_no_data')}</h3></body>")
                return
            title_txt = "Makroekonomik Risk Analizi" if self.current_lang == 'tr' else "Macroeconomic Risk Analysis"
            fig.update_layout(
                title=dict(text=f"<b>{title_txt}</b>", font=dict(size=14, color='#c0392b')),
                xaxis=dict(title='Yıl' if self.current_lang == 'tr' else 'Year', showgrid=True, gridcolor='#ecf0f1', dtick=2),
                yaxis=dict(title='Değer / Oran' if self.current_lang == 'tr' else 'Value / Ratio', showgrid=True, gridcolor='#ecf0f1'),
                paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
                margin=dict(l=50, r=20, t=60, b=80),
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='top', y=-0.12, xanchor='center', x=0.5, font=dict(size=10)),
                template='plotly_white' if self.current_theme == 'light' else 'plotly_dark'
            )
            _load_plotly_to_view(self.risk_web, fig)
            is_en = self.current_lang == 'en'
            src_lbl = 'Risk Indicators Data Source:' if is_en else 'Risk Göstergeleri Veri Kaynağı:'
            latest_lbl = 'Latest Value' if is_en else 'En Güncel Veri'
            rows = []
            for ind in active_inds:
                meta = self._get_metadata(ind)
                rows.append(f"<li style='margin-bottom:8px;'><span style='color:#e74c3c; font-weight:bold;'>■ {ind_names.get(ind, ind)}</span> — {meta[1]}<br>{meta[2]}</li>")
            n_html = f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:12px; color:#2c3e50; line-height:1.5;">
                <div style="margin-bottom:8px;">
                    <b style="color:#e74c3c;">📂 {src_lbl}</b>
                    <ul style="list-style-type:none; padding-left:5px; margin-top:5px;">{''.join(rows)}</ul>
                </div>
            """
            if len(c_displays) == 1:
                last_vals = []
                c_en = self._en_country(c_displays[0])
                cdf = self.df[self.df['Ülke'] == c_en].sort_values('Yıl')
                for ind in active_inds:
                    if not cdf.empty and ind in cdf.columns:
                        v_df = cdf.dropna(subset=[ind])
                        if not v_df.empty:
                            v = v_df.iloc[-1][ind]
                            last_vals.append(f"<b>{ind_names.get(ind, ind)}:</b> {v:.1f}")
                sum_text = f"<hr style='border:0; border-top:1px solid #eee;'><div style='margin-top:8px;'><b>{c_displays[0]}</b> {latest_lbl.lower()}:<br>"
                sum_text += " | ".join(last_vals) + "</div>"
                n_html += sum_text
            n_html += "</div>"
            self.risk_narrative.setHtml(n_html)
        except Exception as e:
            import traceback; traceback.print_exc()
