"""
page_sectoral.py — Mixin: Sektörel Paylar (Page 7)
draw_sectoral_chart
"""
import plotly.graph_objects as go
from sbf_terminal.utils import _load_plotly_to_view


class SectoralMixin:
    """Page 7 — Sektörel Paylar."""

    def draw_sectoral_chart(self):
        try:
            if self.df is None:
                return
            c_displays = self.sec_c.checkedItems() if hasattr(self.sec_c, 'checkedItems') else [self.sec_c.currentText()]
            c_displays = [c for c in c_displays if c != self.t('no_country')]
            if not c_displays:
                return
            s_year, e_year = self.sec_start.currentText(), self.sec_end.currentText()
            try:
                sy, ey = int(s_year), int(e_year)
            except Exception:
                sy, ey = 2000, 2024
            mapping = {
                "Tarım Payı": "Tarım", "Sanayi Payı": "Sanayi", "Hizmetler Payı": "Hizmetler",
                "İmalat Payı": "İmalat", "Enerji-Maden": "Enerji-Maden", "Demir-Çelik": "Demir-Çelik",
                "Otomotiv-Makine": "Otomotiv-Makine", "Lojistik": "Lojistik",
                "İletişim-ICT": "İletişim-ICT", "Finans-Sigorta": "Finans-Sigorta",
                "Agriculture Share": "Tarım", "Industry Share": "Sanayi", "Services Share": "Hizmetler",
                "Manufacturing Share": "İmalat", "Energy-Mining": "Enerji-Maden",
                "Iron-Steel": "Demir-Çelik", "Automotive-Machinery": "Otomotiv-Makine",
                "Logistics": "Lojistik", "ICT Services": "İletişim-ICT", "Finance-Insurance": "Finans-Sigorta"
            }
            active_inds_disp = self.sec_ind.checkedItems()
            active_inds = [mapping.get(d, d) for d in active_inds_disp]
            if not active_inds:
                self.sec_web.setHtml("<body><h3 style='color:red; text-align:center;'>Lütfen en az bir sektör seçiniz.</h3></body>")
                return
            fig = go.Figure()
            sec_colors = {
                'Tarım': '#27ae60', 'Sanayi': '#2980b9', 'Hizmetler': '#f39c12', 'İmalat': '#c0392b',
                'Enerji-Maden': '#16a085', 'Demir-Çelik': '#7f8c8d', 'Otomotiv-Makine': '#d35400',
                'Lojistik': '#3498db', 'İletişim-ICT': '#8e44ad', 'Finans-Sigorta': '#2c3e50'
            }
            colors_list = ['#2980b9', '#e74c3c', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#16a085', '#34495e']
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
                            if len(c_displays) == 1:
                                color = sec_colors.get(ind, colors_list[i_idx % len(colors_list)])
                                trace_name = ind_names.get(ind, ind)
                                line_style = 'solid'
                            else:
                                color = colors_list[idx % len(colors_list)]
                                trace_name = f"{c_disp} - {ind_names.get(ind, ind)}"
                                line_style = 'solid' if i_idx == 0 else 'dash'
                            fig.add_trace(go.Scatter(
                                x=temp['Yıl'], y=temp[ind],
                                name=trace_name, mode='lines+markers',
                                line=dict(width=2, dash=line_style, color=color),
                                marker=dict(size=6, color=color)
                            ))
            if not has_data:
                self.sec_web.setHtml(f"<body><h3 style='color:gray; text-align:center;'>{self.t('desc_no_data')}</h3></body>")
                return
            title_txt = "Sektörel Paylar (% GSYİH)" if self.current_lang == 'tr' else "Sectoral Shares (% of GDP)"
            fig.update_layout(
                title=dict(text=f"<b>{title_txt}</b>", font=dict(size=14, color='#1a5276')),
                xaxis=dict(title='Yıl' if self.current_lang == 'tr' else 'Year', showgrid=True, gridcolor='#ecf0f1', dtick=2),
                yaxis=dict(title='% GSYİH' if self.current_lang == 'tr' else '% GDP', showgrid=True, gridcolor='#ecf0f1'),
                paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
                margin=dict(l=50, r=20, t=60, b=80),
                hovermode='x unified', hoverlabel=dict(font_size=13),
                legend=dict(orientation='h', yanchor='top', y=-0.12, xanchor='center', x=0.5, font=dict(size=10)),
                template='plotly_white' if self.current_theme == 'light' else 'plotly_dark'
            )
            _load_plotly_to_view(self.sec_web, fig)
            is_en = self.current_lang == 'en'
            src_lbl = 'Data Source:' if is_en else 'Veri Kaynağı:'
            latest_lbl = 'Latest Value' if is_en else 'En Güncel Veri'
            rows = []
            for ind in active_inds:
                meta = self._get_metadata(ind)
                color = sec_colors.get(ind, '#2c3e50')
                rows.append(f"<li style='margin-bottom:8px;'><span style='color:{color}; font-weight:bold;'>■ {ind_names.get(ind, ind)}</span><br>{meta[2]}</li>")
            n_html = f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:12px; color:#2c3e50; line-height:1.5;">
                <div style="margin-bottom:8px;"><b style="color:#27ae60;">📂 {src_lbl}</b>
                <ul style="list-style-type:none; padding-left:5px; margin-top:5px;">{''.join(rows)}</ul></div>
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
                            last_vals.append(f"<b>{ind_names.get(ind, ind)}:</b> {v:.1f}%")
                sum_text = f"<hr style='border:0; border-top:1px solid #eee;'><div style='margin-top:8px;'><b>{c_displays[0]}</b> {latest_lbl.lower()}:<br>"
                sum_text += " | ".join(last_vals) + "</div>"
                n_html += sum_text
            else:
                msg = f"{len(c_displays)} countries selected." if is_en else f"{len(c_displays)} ülke seçildi."
                n_html += f"<hr style='border:0; border-top:1px solid #eee;'><div style='padding-top:8px;'><i>{msg}</i></div>"
            n_html += "</div>"
            self.sec_narrative.setHtml(n_html)
        except Exception as e:
            import traceback; traceback.print_exc()
