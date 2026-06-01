"""
page_rankings.py — Mixin: Küresel Sıralamalar (Page 4)
plot_blocks
"""
import plotly.graph_objects as go
from sbf_terminal.utils import _load_plotly_to_view, get_econ_fmt


class RankingsMixin:
    """Page 4 — Küresel Sıralamalar."""

    def plot_blocks(self):
        if self.df is None:
            return
        ind_display = self.blk_cmb.currentText()
        if not ind_display:
            return
        ind = self._resolve_ind(ind_display)
        if self.blk_price.currentText() == "Nominal" and ind in ['GSYİH', 'GSMH', 'Kişi Başı GSYİH', 'Kişi Başı GSMH']:
            if ind + '_Nominal' in self.df.columns:
                ind = ind + '_Nominal'
        try:
            y = int(self.blk_year.currentText())
        except Exception:
            y = 2024
        df_y = self.df[(self.df['Yıl'] == y)].copy()
        if 'region' in df_y.columns:
            df_y = df_y[df_y['region'].notna() & (df_y['region'] != '')]
        if df_y.columns.duplicated().any():
            df_y = df_y.loc[:, ~df_y.columns.duplicated(keep='first')]
        df_y = df_y.dropna(subset=[ind]).sort_values(ind, ascending=False).head(150)
        if df_y.empty:
            return
        df_y['Rank'] = range(1, len(df_y) + 1)
        top_all = df_y.iloc[::-1]
        display_countries = [f"#{r}  {self._display_country(c)}" for r, c in zip(top_all['Rank'], top_all['Ülke'])]
        pf = go.Figure(go.Bar(
            x=top_all[ind], y=display_countries, orientation='h',
            marker=dict(color='#2980b9', line=dict(color='#1c5980', width=0.6)),
            text=[get_econ_fmt(self.current_lang)(v) for v in top_all[ind]],
            textposition='auto',
            cliponaxis=False
        ))
        ind_disp = self.t('ind_names').get(ind, ind)
        chart_height = max(700, len(top_all) * 30)
        title_txt = f"{self.t('nav_block')}: {ind_disp} ({y})"
        min_val = float(top_all[ind].min())
        max_val = float(top_all[ind].max())
        pad_l = (max_val - min_val) * 0.05 if min_val < 0 else 0
        x_range = [min_val - pad_l, max_val]
        pf.update_layout(
            title=dict(text=f"<b>{title_txt}</b>", font=dict(size=16, color='#2c3e50'), x=0.5),
            xaxis=dict(range=x_range, showgrid=True, gridcolor='#ecf0f1', side='top',
                       title=dict(text=self._get_unit_label(ind), font=dict(size=11))),
            yaxis=dict(showgrid=False, automargin=True, tickfont=dict(size=10, family="monospace")),
            paper_bgcolor='#fafafa', plot_bgcolor='#ffffff',
            margin=dict(l=0, r=60, t=80, b=40),
            height=chart_height,
            bargap=0.25
        )
        _load_plotly_to_view(self.blk_web, pf)
        if hasattr(self, 'p4_narrative') and hasattr(self, 'indicator_metadata'):
            meta = self._get_metadata(ind)
            is_en = self.current_lang == 'en'
            ind_name = self.t('ind_names').get(ind_display, ind_display)
            price_lbl = self.blk_price.currentText() if hasattr(self, 'blk_price') else 'Reel'
            price_tag = f" <span style='color:#e67e22;'>(Nominal)</span>" if price_lbl == 'Nominal' else f" <span style='color:#8e44ad;'>({'Real' if is_en else 'Reel'}, 2015)</span>"
            lbl_src = 'Data Sources' if is_en else 'Veri Kaynağı'
            note = f"<li style='margin-bottom:8px;'><span style='color:#2980b9; font-weight:bold;'>■ {ind_name}{price_tag}</span><br>{meta[2]}</li>"
            self.p4_narrative.setHtml(f"""
            <div style="font-family:'Segoe UI', sans-serif; font-size:12px; color:#2c3e50; line-height:1.5;">
                <div style="margin-bottom:8px;"><b style="color:#1a5276;">📚 {lbl_src}</b>
                <ul style="list-style-type:none; padding-left:5px; margin-top:5px;">{note}</ul></div>
            </div>""")
