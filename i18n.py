"""
i18n.py — Çok dilli metin sözlükleri (TR + EN)
"""


LANGS = {
    'tr': {
        'title': 'SBF Makro Veri Analiz Merkezi', 'logo': '🏛️ SBF\nMAKRO TERMİNAL',
        'update_btn': '🌐 Verileri Güncelle', 'nav_map': '🏠 Genel Harita',
        'nav_macro': '📊 Makroekonomi', 'nav_rank': '📊 Küresel Sıralama',
        'nav_ts': '📈 Zaman Serisi Anlz.', 'nav_rd': '🌱 Kalkınma ve Bölüşüm',
        'nav_pub': '🏛️ Kamu Maliyesi', 'nav_block': '📊 Küresel Sıralamalar',
        'nav_bench': '🏁 Ülke Kıyaslama', 'nav_sector': '🏗️ Sektörel Paylar',
        'nav_risk': '⚠️ Risk Analizi', 'nav_corr': '🔗 Korelasyon', 'nav_energy': '⚡ Enerji Ekonomisi',
        'theme_dark': '🌙 Karanlık Mod', 'theme_light': '☀️ Aydınlık Mod',
        'search_placeholder': '🔍 Ülke Seçin veya Arayın...', 'statik_yil': 'Statik Analiz Yılı:',
        'refresh_btn': 'Anlık Yenile', 'clear_btn': 'Ekranı Temizle', 'copy_btn': '📋 Tüm Verileri Kopyala',
        'mode_instant': '📍 Anlık', 'mode_period': '📅 Dönem',
        'rank_title': '📊 KÜRESEL EKONOMİK HASILA SIRALAMASI', 'yil_sec': 'Yıl Seçiniz:',
        'country_lbl': 'Ülke:', 'country1_lbl': 'Ülke 1:', 'country2_lbl': 'Ülke 2:',
        'ind_lbl': 'Gösterge:', 'ind_sel_lbl': 'Gösterge:', 'period_lbl': 'Dönem:',
        'report_btn': '📑 Rapor Al', 'risk_report_btn': '📑 Risk Raporu', 'compare_btn': '📊 Kıyasla',
        'no_country': '--- Ülke Seçiniz ---',
        'rank_h1': 'Sıra', 'rank_h2': 'Ülke', 'rank_h3': 'GSYİH', 'rank_h4': 'Kişi Başı GSYİH',
        'gdp_pc_reel': 'Kişi Başı GSYİH (Reel)', 'gdp_pc_sagp': 'Kişi Başı GSYİH (SAGP/PPP)',
        'gni_pc_reel': 'Kişi Başı GSMH (Reel)', 'gni_pc_sagp': 'Kişi Başı GSMH (SAGP/PPP)',
        'risk_h1': 'Gösterge', 'risk_h2': 'Ülke 1', 'risk_h3': 'Ülke 2', 'risk_h4': 'Grup Ort.',
        'blk_h1': 'Sıra', 'blk_h2': 'Ülke', 'blk_h3': 'Değer', 'blk_h4': 'Dünya Payı %',
        'gdp_rank': 'GSYİH Dünya Sıralaması',
        'gdp_nom': 'GSYİH (Reel, 2015 Sabit Fiyat)', 'gni_nom': 'GSMH (Reel, 2015 Sabit Fiyat)',
        'gdp_pc': 'Kişi Başı GSYİH', 'gni_pc': 'Kişi Başı GSMH',
        'sec_dist': '🏗️ Sektörel Dağılım (% GSYİH)',
        'sec_agr': '🌾 Tarım', 'sec_ind': '🏭 Sanayi', 'sec_srv': '🏢 Hizmet',
        'conj': '📈 Konjonktür & Makro Denge', 'grw': 'GSYİH Büyüme', 'inf': 'Enflasyon (TÜFE)',
        'ipi': 'Sanayi Üretimi (IPI)', 'ppi': 'Üretici Fiyatları (ÜFE)',
        'pub': '🏛️ Kamu Maliyesi ve Harcamalar',
        'kamu_harc': 'Kamu Harcamaları', 'sav_harc': 'Savunma Harcamaları',
        'egitim': 'Eğitim Harcamaları', 'saglik': 'Sağlık Harcamaları',
        'vergi_gel': 'Vergi Gelirleri', 'butce_deng': 'Bütçe Dengesi',
        'dis_borc': 'Dış Borç', 'sosyal_ref': 'Sosyal Refah',
        'unemp': 'İşsizlik Oranı', 'cab': 'Cari İşlemler/GSYİH',
        'hc': '🌱 Kalkınma ve Bölüşüm',
        'hdi': 'İnsani Gelişmişlik', 'ihdi': 'Eşitsizliğe Uyarlanmış İGE (IHDI)',
        'phdi': 'Gezegensel Baskılara Uyarlanmış İGE (PHDI)',
        'gii': 'Toplumsal Cinsiyet Eşitsizliği (GII)', 'gdi': 'Toplumsal Cinsiyet Gelişimi (GDI)',
        'lit': 'Okuryazarlık Oranı', 'gini': 'Gini Katsayısı', 'palma_ratio': 'Palma Oranı',
        'wiid_s10s1_ratio': 'WIID (S10/S1)', 'WIID_Ratio': 'WIID Oranı (S10/S1)',
        'glob_perf': '🏆 Küresel Performans',
        'trill': 'Trilyon', 'bill': 'Milyar',
        'desc_no_data': 'Bu yıl için bu göstergede yeterli veri bulunmamaktadır.',
        'energy_source_text': '<b>KAYNAKÇA:</b> <b>Dünya Bankası WDI</b> (Enerji İthalatı Bağımlılığı) &nbsp;|&nbsp; <b>Our World in Data</b> (Kişi Başı Enerji, Karbon, Fosil, Yenilenebilir Payı)',
        'source': 'Kaynak', 'world_share': 'Dünya Payı', 'leader': 'Lider',
        'risk_map': 'Risk ve Kalkınma Haritası',
        'benchmark': 'Kıyaslama Analizi', 'trend_sum': 'Eğilim Özeti',
        'academic_def': 'Akademik Tanım', 'data_source': 'Veri Kaynağı',
        'fiyat_esitsizlik': 'Fiyat & Eşitsizlik',
        'ineq_chart_hdr': '◉ Eşitsizlik Karşılaştırma Grafiği',
        'bullet_chart_title': '◉ Karşılaştırmalı Analiz Paneli',
        'ineq_chart_title': 'Eşitsizlik ve İnsani Gelişmişlik Trendleri',
        'ratio_scale': 'Rasyo Ölçeği (WIID/Palma)', 'year': 'Yıl',
        'no_gini_data': 'Ülke seçiniz veya\nveri bulunamadı',
        'price_type_lbl': 'Fiyat Türü:', 'base_year_lbl': 'Baz Yılı:',
        'rank_narrative': (
            "{y} yılında listelenen ilk 100 ekonomi arasında birinci sırada yer alan "
            "<span style='color:#27ae60; font-weight:bold;'>{leader}</span>, izlenen küresel ekonomik "
            "hasılanın yaklaşık <span style='font-weight:bold;'>%{share:.1f}</span>'lik dilimini "
            "kontrol etmektedir. Sıralama nominal GSYİH büyüklüğüne göre hiyerarşik olarak dizilmiştir."
        ),
        'ts_trend_increase': 'artış', 'ts_trend_decrease': 'düşüş',
        'ts_narrative_1': (
            "Seçili dönemde {ind} göstergesi %{pct:.1f} oranında belirgin bir "
            "<span style='color:{color}; font-weight:bold;'>{trend_word} trendi</span> sergilemiştir."
        ),
        'ts_narrative_zero': 'Veri sıfır bazlı değişim göstermiştir.',
        'ts_narrative_nodata': 'Trend analizi için yeterli veri noktası bulunmuyor (eksik veriler mevcut).',
        'ts_narrative_err': 'Trend hesaplanırken bir hata oluştu ({err}).',
        'blk_narrative': (
            "{ind} göstergesi özelinde seçili yılda <span style='color:#27ae60; font-weight:bold;'>{leader}</span>, "
            "dünya toplam değerinin yaklaşık <span style='font-weight:bold;'>%{share:.1f}</span>'ini tek başına "
            "oluşturarak küresel blok liderliğini elde etmiştir."
        ),
        'bm_narrative': (
            "Yukarıdaki zaman serisi ağında o yılın zirve noktasını oluşturan eğri, "
            "<span style='color:#27ae60; font-weight:bold;'>{ind}</span> göstergesi açısından "
            "referans grup içerisindeki baskın ekonomiyi temsil etmektedir."
        ),
        'risk_def_title': 'Akademik Tanım (Kalkınma Risk Matrisi):',
        'risk_def_text': (
            "İki ülkenin temel makroekonomik metriklerinin görsel karşılaştırmasını sunar. "
            "Bullet chart'ta mavi çubuk = Ülke 1, kırmızı çubuk = Ülke 2, dikey siyah çizgi = Grup Ortalaması."
        ),
        'risk_data_reading': 'Veri Okuması',
        'risk_prod_price': 'Üretim & Fiyat End.',
        'risk_dev_gender': 'Kalkınma & Cinsiyet End.',
        'def_not_avail': 'Bu gösterge için akademik tanım mevcut değil.',
        'src_unknown': 'Bilinmeyen Kaynak',
        'blk_items': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
        'blk_display': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
        'ind_names': {
            'GSYİH': 'GSYİH', 'GSMH': 'GSMH', 'Kişi Başı GSYİH': 'Kişi Başı GSYİH',
            'Kişi Başı GSMH': 'Kişi Başı GSMH', 'Enflasyon': 'Enflasyon',
            'İşsizlik': 'İşsizlik', 'Büyüme': 'Büyüme', 'Cari Denge': 'Cari Denge',
            'Borç Oranı': 'Borç Oranı', 'Gini': 'Gini', 'Ar-Ge Yoğunluğu': 'Ar-Ge Yoğunluğu',
            'Genç İşsizlik': 'Genç İşsizlik', 'Karbon': 'Karbon', 'Yaşam Süresi': 'Yaşam Süresi',
            'Eğitim': 'Eğitim', 'Sağlık': 'Sağlık',
            'İnsani Gelişmişlik': 'İnsani Gelişmişlik', 'Yoksulluk': 'Yoksulluk',
            'İhracat': 'İhracat', 'İthalat': 'İthalat', 'Tarım': 'Tarım',
            'Sanayi': 'Sanayi', 'Hizmetler': 'Hizmetler',
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
            'Borç Servisi': 'Borç Servisi / İhracat',
            'Enerji İthalatı Bağımlılığı': 'Enerji İthalatı Bağımlılığı',
            'HDI_UNDP': 'İnsani Gelişme Endeksi (HDI)',
            'IHDI': 'Eşitsizliğe Uyarlanmış İGE (IHDI)',
            'PHDI': 'Gezegensel Baskılara Uyarlanmış İGE (PHDI)',
            'GII': 'Toplumsal Cinsiyet Eşitsizliği (GII)',
            'GDI': 'Toplumsal Cinsiyet Gelişimi (GDI)',
            'palma_ratio': 'Palma Oranı', 'WIID_Ratio': 'WIID Oranı (S10/S1)',
            'Kişi Başı GSYİH (SAGP)': 'Kişi Başı GSYİH (SAGP)',
            'Kişi Başı GSMH (SAGP)': 'Kişi Başı GSMH (SAGP)',
            'Current Account': 'Cari Denge', 'Debt Ratio': 'Borç Oranı',
            'GDP Per Capita': 'Kişi Başı GSYİH', 'GNI Per Capita': 'Kişi Başı GSMH',
            'GDP Per Capita (PPP)': 'Kişi Başı GSYİH (SAGP)',
            'GNI Per Capita (PPP)': 'Kişi Başı GSMH (SAGP)',
            'VDem_Score': 'V-Dem Demokrasi Endeksi',
            'Kişi Başı Enerji (kWh)': 'Kişi Başı Enerji (kWh)',
            'Kişi Başı Karbon (Ton)': 'Kişi Başı Karbon (Ton)',
            'Fosil Yakıt Payı (%)': 'Fosil Yakıt Payı (%)',
            'Yenilenebilir Payı (%)': 'Yenilenebilir Payı (%)',
            'Karbon (Milyon Ton)': 'Karbon (Milyon Ton)',
            'Mutlak Yoksulluk (%)': 'Mutlak Yoksulluk (%)',
            'OWID Gini': 'OWID Gini',
        }
    },
    'en': {
        'title': 'SBF Macro Data Analysis Center', 'logo': '🏛️ SBF\nMACRO TERMINAL',
        'update_btn': '🌐 Update Data', 'nav_map': '🏠 General Map',
        'nav_macro': '📊 Macroeconomics', 'nav_rank': '📊 Global Ranking',
        'nav_ts': '📈 Time Series Anlyz.', 'nav_rd': '🌱 Development & Distribution',
        'nav_pub': '🏛️ Public Finance', 'nav_block': '📊 Global Rankings',
        'nav_bench': '🏁 Country Benchmarking', 'nav_sector': '🏗️ Sectoral Shares',
        'nav_risk': '⚠️ Risk Analysis', 'nav_corr': '🔗 Correlation', 'nav_energy': '⚡ Energy Economics',
        'theme_dark': '🌙 Dark Mode', 'theme_light': '☀️ Light Mode',
        'search_placeholder': '🔍 Search or Select Country...', 'statik_yil': 'Static Analysis Year:',
        'refresh_btn': 'Refresh Now', 'clear_btn': 'Clear Screen', 'copy_btn': '📋 Copy All Data',
        'mode_instant': '📍 Instant', 'mode_period': '📅 Period',
        'rank_title': '📊 GLOBAL ECONOMIC OUTPUT RANKING', 'yil_sec': 'Select Year:',
        'country_lbl': 'Country:', 'country1_lbl': 'Country 1:', 'country2_lbl': 'Country 2:',
        'ind_lbl': 'Indicator:', 'ind_sel_lbl': 'Indicator:', 'period_lbl': 'Period:',
        'report_btn': '📑 Export Report', 'risk_report_btn': '📑 Risk Report', 'compare_btn': '📊 Compare',
        'no_country': '--- Select Country ---',
        'rank_h1': 'Rank', 'rank_h2': 'Country', 'rank_h3': 'GDP', 'rank_h4': 'GDP Per Capita',
        'gdp_pc_reel': 'GDP Per Capita (Real)', 'gdp_pc_sagp': 'GDP Per Capita (PPP)',
        'gni_pc_reel': 'GNI Per Capita (Real)', 'gni_pc_sagp': 'GNI Per Capita (PPP)',
        'risk_h1': 'Indicator', 'risk_h2': 'Country 1', 'risk_h3': 'Country 2', 'risk_h4': 'Group Avg.',
        'blk_h1': 'Rank', 'blk_h2': 'Country', 'blk_h3': 'Value', 'blk_h4': 'World Share %',
        'gdp_rank': 'GDP Global Ranking',
        'gdp_nom': 'GDP (Real, 2015 Constant)', 'gni_nom': 'GNI (Real, 2015 Constant)',
        'gdp_pc': 'GDP Per Capita', 'gni_pc': 'GNI Per Capita',
        'sec_dist': '🏗️ Sectoral Dist. (% GDP)',
        'sec_agr': '🌾 Agriculture', 'sec_ind': '🏭 Industry', 'sec_srv': '🏢 Services',
        'conj': '📈 Conjuncture & Macro Balance', 'grw': 'GDP Growth', 'inf': 'Inflation (CPI)',
        'ipi': 'Industrial Production (IPI)', 'ppi': 'Producer Price Index (PPI)',
        'pub': '🏛️ Public Finance & Expenditures',
        'kamu_harc': 'Gov. Expenditure', 'sav_harc': 'Military Exp.',
        'egitim': 'Education Exp.', 'saglik': 'Health Exp.',
        'vergi_gel': 'Tax Revenue', 'butce_deng': 'Budget Balance',
        'dis_borc': 'External Debt', 'sosyal_ref': 'Social Protection',
        'unemp': 'Unemployment Rate', 'cab': 'Current Account/GDP',
        'hc': '🌱 Development & Distribution',
        'hdi': 'Human Development Index', 'ihdi': 'Inequality-adjusted HDI',
        'phdi': 'Planetary pressures-adjusted HDI',
        'gii': 'Gender Inequality Index (GII)', 'gdi': 'Gender Development Index (GDI)',
        'lit': 'Literacy Rate', 'gini': 'Gini Coefficient', 'palma_ratio': 'Palma Ratio',
        'wiid_s10s1_ratio': 'WIID (S10/S1)', 'WIID_Ratio': 'WIID Ratio (S10/S1)',
        'glob_perf': '🏆 Global Performance',
        'trill': 'Trillion', 'bill': 'Billion',
        'desc_no_data': 'Insufficient data for this indicator in the selected year.',
        'energy_source_text': '<b>SOURCES:</b> <b>World Bank WDI</b> (Net Energy Imports) &nbsp;|&nbsp; <b>Our World in Data</b> (Energy per Capita, Carbon, Fossil, Renewable Share)',
        'source': 'Source', 'world_share': 'World Share', 'leader': 'Leader',
        'risk_map': 'Risk and Development Map',
        'benchmark': 'Benchmarking Analysis', 'trend_sum': 'Trend Summary',
        'academic_def': 'Academic Definition', 'data_source': 'Data Source',
        'fiyat_esitsizlik': 'Price & Inequality',
        'ineq_chart_hdr': '◉ Inequality Comparison Chart',
        'bullet_chart_title': '◉ Comparative Analysis Panel',
        'ineq_chart_title': 'Inequality and Human Development Trends',
        'ratio_scale': 'Ratio Scale (WIID/Palma)', 'year': 'Year',
        'no_gini_data': 'Select country or\nno data found',
        'price_type_lbl': 'Price Type:', 'base_year_lbl': 'Base Year:',
        'rank_narrative': (
            "In {y}, ranking first among the top 100 listed economies, "
            "<span style='color:#27ae60; font-weight:bold;'>{leader}</span> controls approximately "
            "<span style='font-weight:bold;'>{share:.1f}%</span> of the tracked global economic output. "
            "The ranking is hierarchically arranged based on nominal GDP."
        ),
        'ts_trend_increase': 'increasing', 'ts_trend_decrease': 'decreasing',
        'ts_narrative_1': (
            "During the selected period, the {ind} indicator exhibited a significant "
            "<span style='color:{color}; font-weight:bold;'>{trend_word} trend</span> of {pct:.1f}%."
        ),
        'ts_narrative_zero': 'The data showed a zero-based change.',
        'ts_narrative_nodata': 'Not enough data points available for trend analysis (missing data).',
        'ts_narrative_err': 'An error occurred while calculating the trend ({err}).',
        'blk_narrative': (
            "For the {ind} indicator in the selected year, "
            "<span style='color:#27ae60; font-weight:bold;'>{leader}</span> achieved global block leadership "
            "by singularly accounting for approximately <span style='font-weight:bold;'>{share:.1f}%</span> "
            "of the world's total value."
        ),
        'bm_narrative': (
            "In the time series network above, the curve forming the peak for that year represents the "
            "dominant economy within the reference group in terms of the "
            "<span style='color:#27ae60; font-weight:bold;'>{ind}</span> indicator."
        ),
        'risk_def_title': 'Academic Definition (Development Risk Matrix):',
        'risk_def_text': (
            "Provides a visual comparison of key macroeconomic metrics for two countries. "
            "In the bullet chart, blue bar = Country 1, red bar = Country 2, vertical black line = Group Average."
        ),
        'risk_data_reading': 'Data Reading',
        'risk_prod_price': 'Production & Price Ind.',
        'risk_dev_gender': 'Development & Gender Ind.',
        'def_not_avail': 'No academic definition available for this indicator.',
        'src_unknown': 'Unknown Source',
        'blk_items': ['GSYİH', 'Büyüme', 'Enflasyon', 'Borç Oranı', 'Cari Denge', 'Ar-Ge Yoğunluğu'],
        'blk_display': ['GDP', 'Growth', 'Inflation', 'Debt Ratio', 'Current Account', 'R&D Intensity'],
        'ind_names': {
            'GSYİH': 'GDP', 'GSMH': 'GNI', 'Kişi Başı GSYİH': 'GDP Per Capita',
            'Kişi Başı GSMH': 'GNI Per Capita', 'Enflasyon': 'Inflation',
            'İşsizlik': 'Unemployment', 'Büyüme': 'Growth', 'Cari Denge': 'Current Account',
            'Borç Oranı': 'Debt Ratio', 'Gini': 'Gini', 'Ar-Ge Yoğunluğu': 'R&D Intensity',
            'Genç İşsizlik': 'Youth Unemployment', 'Karbon': 'Carbon',
            'Yaşam Süresi': 'Life Expectancy', 'Eğitim': 'Education', 'Sağlık': 'Health',
            'İnsani Gelişmişlik': 'Human Development Index', 'Yoksulluk': 'Poverty',
            'İhracat': 'Exports', 'İthalat': 'Imports', 'Tarım': 'Agriculture',
            'Sanayi': 'Industry', 'Hizmetler': 'Services',
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
            'Borç Servisi': 'Debt Service / Exports',
            'Enerji İthalatı Bağımlılığı': 'Energy Imports',
            'HDI_UNDP': 'Human Development Index (HDI)',
            'IHDI': 'Inequality-adjusted HDI',
            'PHDI': 'Planetary pressures-adjusted HDI',
            'GII': 'Gender Inequality Index (GII)',
            'GDI': 'Gender Development Index (GDI)',
            'palma_ratio': 'Palma Ratio', 'WIID_Ratio': 'WIID Ratio (S10/S1)',
            'Kişi Başı GSYİH (SAGP)': 'GDP Per Capita (PPP)',
            'Kişi Başı GSMH (SAGP)': 'GNI Per Capita (PPP)',
            'Current Account': 'Current Account', 'Debt Ratio': 'Debt Ratio',
            'GDP Per Capita': 'GDP Per Capita', 'GNI Per Capita': 'GNI Per Capita',
            'GDP Per Capita (PPP)': 'GDP Per Capita (PPP)',
            'GNI Per Capita (PPP)': 'GNI Per Capita (PPP)',
            'GDP': 'GDP', 'GNI': 'GNI', 'Inflation': 'Inflation',
            'Growth': 'Growth', 'Unemployment': 'Unemployment',
            'VDem_Score': 'V-Dem Democracy Index',
            'Kişi Başı Enerji (kWh)': 'Energy per Capita (kWh)',
            'Kişi Başı Karbon (Ton)': 'Carbon per Capita (Tonnes)',
            'Fosil Yakıt Payı (%)': 'Fossil Fuel Share (%)',
            'Yenilenebilir Payı (%)': 'Renewables Share (%)',
            'Karbon (Milyon Ton)': 'Carbon (Million Tonnes)',
            'Mutlak Yoksulluk (%)': 'Absolute Poverty (%)',
            'OWID Gini': 'OWID Gini',
        }
    }
}


def get_text(lang, key, default=None):
    """Belirtilen dil ve anahtar için metin döndürür."""
    d = LANGS.get(lang, LANGS['tr'])
    if default is None:
        default = key
    return d.get(key, default)
