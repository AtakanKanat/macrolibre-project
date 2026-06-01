"""
constants.py — Sabit veriler ve yol tanımları
COUNTRY_TR sözlüğü, INDICATORS ve dosya yolları burada tanımlanır.
"""
import os

# ── Yol Sabitleri ─────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parquet_path = os.path.join(current_dir, "macro_data_25y.parquet")
social_csv_path = os.path.join(current_dir, "social_indicators.csv")
blacklist_path = os.path.join(current_dir, "timeout_blacklist.json")

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --disable-gpu-shader-disk-cache"

# ── EN → TR Ülke Adı Sözlüğü ──────────────────────────────────────────────────
COUNTRY_TR = {
    "Afghanistan": "Afganistan", "Albania": "Arnavutluk", "Algeria": "Cezayir",
    "Angola": "Angola", "Argentina": "Arjantin", "Armenia": "Ermenistan",
    "Australia": "Avustralya", "Austria": "Avusturya", "Azerbaijan": "Azerbaycan",
    "Bahamas, The": "Bahamalar", "Bahrain": "Bahreyn", "Bangladesh": "Bangladeş",
    "Barbados": "Barbados", "Belarus": "Belarus", "Belgium": "Belçika",
    "Belize": "Belize", "Benin": "Benin", "Bolivia": "Bolivya",
    "Bosnia and Herzegovina": "Bosna-Hersek", "Botswana": "Botsvana",
    "Brazil": "Brezilya", "Brunei Darussalam": "Brunei",
    "Bulgaria": "Bulgaristan", "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi", "Cabo Verde": "Yeşil Burun", "Cambodia": "Kamboçya",
    "Cameroon": "Kamerun", "Canada": "Kanada",
    "Central African Republic": "Orta Afrika Cumhuriyeti", "Chad": "Çad",
    "Chile": "Şili", "China": "Çin", "Colombia": "Kolombiya",
    "Comoros": "Komorlar", "Congo, Dem. Rep.": "Kongo Demokratik Cumhuriyeti",
    "Congo, Rep.": "Kongo Cumhuriyeti", "Costa Rica": "Kosta Rika",
    "Cote d'Ivoire": "Fildişi Sahili", "Croatia": "Hırvatistan",
    "Cuba": "Küba", "Cyprus": "Kıbrıs", "Czech Republic": "Çekya",
    "Czechia": "Çekya", "Denmark": "Danimarka", "Djibouti": "Cibuti",
    "Dominican Republic": "Dominik Cumhuriyeti", "Ecuador": "Ekvador",
    "Egypt, Arab Rep.": "Mısır", "El Salvador": "El Salvador",
    "Equatorial Guinea": "Ekvator Ginesi", "Eritrea": "Eritre",
    "Estonia": "Estonya", "Eswatini": "Esvatini", "Ethiopia": "Etiyopya",
    "Fiji": "Fiji", "Finland": "Finlandiya", "France": "Fransa",
    "Gabon": "Gabon", "Gambia, The": "Gambiya", "Georgia": "Gürcistan",
    "Germany": "Almanya", "Ghana": "Gana", "Greece": "Yunanistan",
    "Guatemala": "Guatemala", "Guinea": "Gine",
    "Guinea-Bissau": "Gine-Bissau", "Guyana": "Guyana", "Haiti": "Haiti",
    "Honduras": "Honduras", "Hong Kong SAR, China": "Hong Kong",
    "Hungary": "Macaristan", "Iceland": "İzlanda", "India": "Hindistan",
    "Indonesia": "Endonezya", "Iran, Islamic Rep.": "İran", "Iraq": "Irak",
    "Ireland": "İrlanda", "Israel": "İsrail", "Italy": "İtalya",
    "Jamaica": "Jamaika", "Japan": "Japonya", "Jordan": "Ürdün",
    "Kazakhstan": "Kazakistan", "Kenya": "Kenya",
    "Korea, Dem. People's Rep.": "Kuzey Kore", "Korea, Rep.": "Güney Kore",
    "Kosovo": "Kosova", "Kuwait": "Kuveyt",
    "Kyrgyz Republic": "Kırgızistan", "Lao PDR": "Laos", "Latvia": "Letonya",
    "Lebanon": "Lübnan", "Lesotho": "Lesoto", "Liberia": "Liberya",
    "Libya": "Libya", "Lithuania": "Litvanya", "Luxembourg": "Lüksemburg",
    "Macao SAR, China": "Makao", "Madagascar": "Madagaskar",
    "Malawi": "Malavi", "Malaysia": "Malezya", "Maldives": "Maldivler",
    "Mali": "Mali", "Malta": "Malta", "Mauritania": "Moritanya",
    "Mauritius": "Mauritius", "Mexico": "Meksika", "Moldova": "Moldova",
    "Mongolia": "Moğolistan", "Montenegro": "Karadağ", "Morocco": "Fas",
    "Mozambique": "Mozambik", "Myanmar": "Myanmar", "Namibia": "Namibya",
    "Nepal": "Nepal", "Netherlands": "Hollanda", "New Zealand": "Yeni Zelanda",
    "Nicaragua": "Nikaragua", "Niger": "Nijer", "Nigeria": "Nijerya",
    "North Macedonia": "Kuzey Makedonya", "Norway": "Norveç", "Oman": "Umman",
    "Pakistan": "Pakistan", "Panama": "Panama",
    "Papua New Guinea": "Papua Yeni Gine", "Paraguay": "Paraguay",
    "Peru": "Peru", "Philippines": "Filipinler", "Poland": "Polonya",
    "Portugal": "Portekiz", "Qatar": "Katar", "Romania": "Romanya",
    "Russian Federation": "Rusya", "Rwanda": "Ruanda",
    "Sao Tome and Principe": "Sao Tome ve Principe",
    "Saudi Arabia": "Suudi Arabistan", "Senegal": "Senegal",
    "Serbia": "Sırbistan", "Seychelles": "Seyşeller",
    "Sierra Leone": "Sierra Leone", "Singapore": "Singapur",
    "Slovak Republic": "Slovakya", "Slovenia": "Slovenya",
    "Solomon Islands": "Solomon Adaları", "Somalia": "Somali",
    "South Africa": "Güney Afrika", "South Sudan": "Güney Sudan",
    "Spain": "İspanya", "Sri Lanka": "Sri Lanka", "Sudan": "Sudan",
    "Suriname": "Surinam", "Sweden": "İsveç", "Switzerland": "İsviçre",
    "Syrian Arab Republic": "Suriye", "Taiwan, China": "Tayvan", "Taiwan": "Tayvan",
    "North Korea": "Kuzey Kore",
    "Tajikistan": "Tacikistan", "Tanzania": "Tanzanya", "Thailand": "Tayland",
    "Timor-Leste": "Doğu Timor", "Togo": "Togo", "Tonga": "Tonga",
    "Trinidad and Tobago": "Trinidad ve Tobago", "Tunisia": "Tunus",
    "Turkey": "Türkiye", "Turkiye": "Türkiye",
    "Turkmenistan": "Türkmenistan", "Uganda": "Uganda", "Ukraine": "Ukrayna",
    "United Arab Emirates": "Birleşik Arap Emirlikleri",
    "United Kingdom": "Birleşik Krallık", "United States": "Amerika Birleşik Devletleri",
    "Uruguay": "Uruguay", "Uzbekistan": "Özbekistan", "Vanuatu": "Vanuatu",
    "Venezuela, RB": "Venezuela", "Vietnam": "Vietnam",
    "West Bank and Gaza": "Batı Şeria ve Gazze",
    "Yemen, Rep.": "Yemen", "Zambia": "Zambiya", "Zimbabwe": "Zimbabve",
}

# EN ← TR (ters arama için)
COUNTRY_TR_REV = {v: k for k, v in COUNTRY_TR.items()}

# ── World Bank Gösterge Kodları ────────────────────────────────────────────────
INDICATORS = {
    'NY.GDP.MKTP.CD': 'GSYİH', 'NY.GNP.MKTP.CD': 'GSMH',
    'NY.GDP.MKTP.KD': 'GSYİH (Reel)', 'NY.GNP.MKTP.KD': 'GSMH (Reel)',
    'NY.GDP.PCAP.CD': 'Kişi Başı GSYİH', 'NY.GNP.PCAP.CD': 'Kişi Başı GSMH',
    'NY.GDP.PCAP.KD': 'Kişi Başı GSYİH (Reel)', 'NY.GNP.PCAP.KD': 'Kişi Başı GSMH (Reel)',
    'NY.GDP.PCAP.PP.CD': 'Kişi Başı GSYİH (SAGP)', 'NY.GNP.PCAP.PP.CD': 'Kişi Başı GSMH (SAGP)',
    'SI.POV.GINI': 'Gini', 'FP.CPI.TOTL.ZG': 'Enflasyon',
    'SL.UEM.TOTL.ZS': 'İşsizlik', 'NY.GDP.MKTP.KD.ZG': 'Büyüme',
    'BN.CAB.XOKA.GD.ZS': 'Cari Denge', 'GC.DOD.TOTL.GD.ZS': 'Borç Oranı',
    'SL.UEM.1524.ZS': 'Genç İşsizlik', 'EN.ATM.CO2E.PC': 'Karbon',
    'SP.DYN.LE00.IN': 'Yaşam Süresi', 'GB.XPD.RSDV.GD.ZS': 'Ar-Ge Yoğunluğu',
    'SE.XPD.TOTL.GD.ZS': 'Eğitim', 'SH.XPD.CHEX.GD.ZS': 'Sağlık',
    'SI.POV.DDAY': 'Yoksulluk', 'NE.EXP.GNFS.ZS': 'İhracat',
    'NE.IMP.GNFS.ZS': 'İthalat', 'NV.AGR.TOTL.ZS': 'Tarım',
    'NV.IND.TOTL.ZS': 'Sanayi', 'NV.SRV.TOTL.ZS': 'Hizmetler',
    'NV.IND.MANF.ZS': 'İmalat', 'NY.GDP.TOTL.RT.ZS': 'Enerji-Maden',
    'EG.IMP.CONS.ZS': 'Enerji İthalatı Bağımlılığı',
    'TX.VAL.MMTL.ZS.UN': 'Demir-Çelik', 'NV.MNF.MTRN.ZS.UN': 'Otomotiv-Makine',
    'TX.VAL.TRAN.ZS.WT': 'Lojistik', 'BX.GSR.CCIS.ZS': 'İletişim-ICT',
    'BX.GSR.INSF.ZS': 'Finans-Sigorta', 'FR.INR.RISK': 'Risk Primi',
    'FI.RES.TOTL.MO': 'İthalat Karşılama', 'DT.DOD.DSTC.IR.ZS': 'Kısa Vadeli Borç',
    'BX.KLT.DINV.WD.GD.ZS': 'DYY-Girişi', 'PX.REX.REER': 'REK',
    'FR.INR.RINR': 'Reel Faiz', 'GC.NLD.TOTL.GD.ZS': 'Bütçe Dengesi',
    'DT.TDS.DECT.EX.ZS': 'Borç Servisi', 'SE.ADT.LITR.ZS': 'Okuryazarlık',
    'NE.CON.GOVT.ZS': 'Kamu Harcamaları', 'MS.MIL.XPND.GD.ZS': 'Savunma Harcamaları',
    'GC.TAX.TOTL.GD.ZS': 'Vergi Gelirleri', 'DT.DOD.DECT.GN.ZS': 'Dış Borç',
    'HD.HCI.OVRL': 'İnsani Gelişmişlik',
    'SI.DST.10TH.10': 'Top10', 'SI.DST.FRST.10': 'Bottom10',
    'SI.DST.FRST.20': 'Low20', 'SI.DST.02ND.20': 'Sec20'
}
