"""
metadata.py — Gösterge metadata sözlükleri (TR + EN)
Her gösterge için birim, tanım ve kaynak bilgisi.
"""

# ── Türkçe Metadata ────────────────────────────────────────────────────────────
INDICATOR_METADATA = {
    'GSYİH': {
        'tanim': 'Bir ekonomide belirli bir dönemde cari fiyatlarla üretilen nihai mal ve hizmetlerin toplam piyasa değeridir.',
        'birim': '$',
        'metodoloji': 'World Bank (NY.GDP.MKTP.CD)'
    },
    'GSYİH (Reel)': {
        'tanim': 'Enflasyon etkisinden arındırılmış, sabit baz yılı fiyatlarıyla ölçülen üretim hacmidir.',
        'birim': '$',
        'metodoloji': 'World Bank (NY.GDP.MKTP.KD)'
    },
    'GSMH': ('Gayri Safi Milli Hasıla (Nominal)', 'Ülke vatandaşlarının yurtiçi ve yurtdışında ürettiği toplam değerdir.', 'World Bank (NY.GNP.MKTP.CD)'),
    'GSMH (Reel)': ('Reel GSMH (2015 Sabit Fiyatlar)', 'Enflasyondan arındırılmış Gayri Safi Milli Hasıla.', 'World Bank (NY.GNP.MKTP.KD)'),
    'Kişi Başı GSYİH': {
        'tanim': 'Toplam nominal yurt içi hasılanın nüfusa bölünmesiyle elde edilen ortalama gelirdir.',
        'birim': '$',
        'metodoloji': 'World Bank (NY.GDP.PCAP.CD)'
    },
    'Kişi Başı GSYİH (Reel)': {
        'tanim': 'Enflasyon etkisinden arındırılmış, sabit baz yılı fiyatlarıyla kişi başı ortalama gelir.',
        'birim': '$ (2015 Sabit Fiyatlar)',
        'metodoloji': 'World Bank (NY.GDP.PCAP.KD)'
    },
    'Kişi Başı GSMH': ('Kişi Başı GSMH (Nominal)', 'Toplam nominal GSMH\'nin nüfusa bölünmesiyle elde edilen ortalama gelirdir.', 'World Bank (NY.GNP.PCAP.CD)'),
    'Kişi Başı GSMH (Reel)': ('Kişi Başı GSMH (Reel)', 'Toplam reel GSMH\'nin nüfusa bölünmesiyle elde edilen ortalama gelirdir.', 'World Bank (NY.GNP.PCAP.KD)'),
    'Kişi Başı GSYİH (SAGP)': ('Kişi Başı GSYİH (SAGP)', 'Satın alma gücü paritesine göre düzeltilmiş kişi başı GSYİH.', 'World Bank (NY.GDP.PCAP.PP.CD)'),
    'Kişi Başı GSMH (SAGP)': ('Kişi Başı GSMH (SAGP)', 'Satın alma gücü paritesine göre düzeltilmiş kişi başı GSMH.', 'World Bank (NY.GNP.PCAP.PP.CD)'),
    'Enflasyon': {
        'tanim': 'Genel fiyat düzeyindeki sürekli artış eğilimidir.',
        'birim': '%',
        'metodoloji': 'World Bank (FP.CPI.TOTL.ZG)'
    },
    'İşsizlik': {
        'tanim': 'Cari ücret düzeyinde çalışmaya hazır ve istekli olduğu halde istihdam edilemeyen atıl işgücü kapasitesidir.',
        'birim': '% (İşgücüne Oran)',
        'metodoloji': 'World Bank (SL.UEM.TOTL.ZS)'
    },
    'Büyüme': {
        'tanim': 'Reel gayrisafi yurt içi hasılanın bir önceki yıla göre oransal artışıdır.',
        'birim': '%',
        'metodoloji': 'World Bank (NY.GDP.MKTP.KD.ZG)'
    },
    'Cari Denge': {
        'tanim': 'Bir ülkenin dış dünyayla olan ticari ve mali işlemlerinin neticesidir.',
        'birim': '%',
        'metodoloji': 'World Bank (BN.CAB.XOKA.GD.ZS)'
    },
    'Borç Oranı': ('Merkezi Yönetim Borcu (% GSYİH)', 'Devletin toplam borcunun milli gelire oranıdır.', 'World Bank (GC.DOD.TOTL.GD.ZS)'),
    'Gini': {
        'tanim': 'Gelir veya servet dağılımındaki adaletsizliğin temel istatistiksel ölçütüdür.',
        'birim': 'Endeks Değeri',
        'metodoloji': 'World Bank (SI.POV.GINI)'
    },
    'Ar-Ge Yoğunluğu': {
        'tanim': 'İnovasyon ve teknoloji üretimine tahsis edilen makroekonomik kaynakların payıdır.',
        'birim': '% (GSYİH)',
        'metodoloji': 'World Bank (GB.XPD.RSDV.GD.ZS)'
    },
    'Genç İşsizlik': ('Genç İşsizlik Oranı (15-24 Yaş)', 'Genç nüfus içerisindeki işsizlik oranını ifade eder.', 'World Bank (SL.UEM.1524.ZS)'),
    'Karbon': ('Kişi Başı Karbon Salınımı', 'Kişi başına düşen metrik ton cinsinden karbondioksit emisyonudur.', 'World Bank (EN.ATM.CO2E.PC)'),
    'Yaşam Süresi': ('Doğuşta Beklenen Yaşam Süresi', 'Yeni doğan bir bireyin mevcut ölüm oranlarına göre beklenen ortalama ömrüdür.', 'World Bank (SP.DYN.LE00.IN)'),
    'Eğitim': ('Eğitim Harcamaları (% GSYİH)', 'Kamu eğitim harcamalarının toplam milli gelire oranıdır.', 'World Bank (SE.XPD.TOTL.GD.ZS)'),
    'Sağlık': ('Sağlık Harcamaları (% GSYİH)', 'Kamu ve özel sağlık harcamalarının toplam milli gelire oranıdır.', 'World Bank (SH.XPD.CHEX.GD.ZS)'),
    'İmalat': ('İmalat Sanayi (% GSYİH)', 'İmalat sanayi üretiminin milli gelir içindeki payıdır.', 'World Bank (NV.IND.MANF.ZS)'),
    'Enerji-Maden': ('Doğal Kaynak Rantı (% GSYİH)', 'Petrol, doğalgaz, kömür ve madenlerden elde edilen toplam rantın milli gelire oranıdır.', 'World Bank (NY.GDP.TOTL.RT.ZS)'),
    'Demir-Çelik': ('Metal ve Maden İhracatı (% Mal İhracı)', 'Demir-çelik ve diğer metal cevherlerinin toplam mal ihracatı içindeki payıdır.', 'World Bank (TX.VAL.MMTL.ZS.UN)'),
    'Otomotiv-Makine': ('Ulaşım ve Makine (% İmalat)', 'Ulaşım araçları ve makine üretiminin toplam imalat katma değeri içindeki payıdır.', 'World Bank (NV.MNF.MTRN.ZS.UN)'),
    'Lojistik': ('Lojistik ve Ulaşım (% Hizmet İhracı)', 'Ulaştırma ve lojistik hizmetlerinin toplam ticari hizmet ihracatı içindeki payıdır.', 'World Bank (TX.VAL.TRAN.ZS.WT)'),
    'İletişim-ICT': ('Bilgi ve İletişim (% Hizmet İhracı)', 'Bilişim ve iletişim teknolojileri hizmetlerinin toplam hizmet ihracatı içindeki payıdır.', 'World Bank (BX.GSR.CCIS.ZS)'),
    'Finans-Sigorta': ('Finans ve Sigorta (% Hizmet İhracı)', 'Finansal hizmetler ve sigortacılık faaliyetlerinin toplam hizmet ihracatı içindeki payıdır.', 'World Bank (BX.GSR.INSF.ZS)'),
    'Cari Açık': ('Cari İşlemler Dengesi (% GSYİH)', 'Cari açık veya fazlanın milli gelire oranıdır.', 'World Bank (BN.CAB.XOKA.GD.ZS)'),
    'Dış Borç-GNI': ('Toplam Dış Borç Stoku (% GSMH)', 'Ülkenin toplam dış borç yükünün Gayri Safi Milli Hasılaya oranıdır.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
    'Risk Primi': ('Ülke Risk Primi (Proxy)', 'Borçlanma faiz oranı ile hazine bonosu faizi arasındaki farktır.', 'World Bank (FR.INR.RISK)'),
    'İthalat Karşılama': ('İthalat Karşılama Süresi (Ay)', 'Toplam rezervlerin mevcut ithalat hacmini kaç ay boyunca karşılayabileceğini gösterir.', 'World Bank (FI.RES.TOTL.MO)'),
    'Kısa Vadeli Borç': ('Kısa Vadeli Dış Borç / Toplam Rezervler', 'Bir yıl içinde ödenecek dış borcun merkez bankası rezervlerine oranıdır.', 'World Bank (DT.DOD.DSTC.IR.ZS)'),
    'DYY-Girişi': ('Doğrudan Yabancı Yatırımlar (% GSYİH)', 'Net yabancı sermaye girişinin milli gelir içindeki payıdır.', 'World Bank (BX.KLT.DINV.WD.GD.ZS)'),
    'REK': ('Reel Efektif Döviz Kuru (REER)', 'Tüketici fiyatlarına göre düzeltilmiş, ticaret ağırlıklı nominal kur endeksidir (2010=100).', 'World Bank (PX.REX.REER)'),
    'Reel Faiz': ('Reel Faiz Oranı (%)', 'Enflasyondan arındırılmış piyasa faiz oranıdır.', 'World Bank (FR.INR.RINR)'),
    'Bütçe Dengesi': ('Bütçe Dengesi (% GSYİH)', 'Merkezi yönetim bütçe açığının veya fazlasının GSYİH içindeki payıdır.', 'World Bank (GC.NLD.TOTL.GD.ZS)'),
    'Borç Servisi': ('Toplam Borç Servisi (% İhracat)', 'Anapara ve faiz ödemelerinin toplam mal ve hizmet ihracatına oranıdır.', 'World Bank (DT.TDS.DECT.EX.ZS)'),
    'İnsani Gelişmişlik': ('İnsani Sermaye Endeksi', 'Bir ülkenin sağlık ve eğitim verilerine dayanarak gelecekteki verimliliğini ölçer.', 'World Bank (HD.HCI.OVRL)'),
    'Yoksulluk': ('Yoksulluk Sınırı', 'Günde belirli bir tutarın altında yaşayan nüfusun yüzdesidir.', 'World Bank (SI.POV.DDAY)'),
    'İhracat': {
        'tanim': 'Bir ülkenin yerleşik kişi ve kurumları tarafından dış dünyaya satılan mal ve hizmetlerin toplam değeri.',
        'birim': 'GSYİH İçindeki Payı (%)',
        'metodoloji': 'World Bank (NE.EXP.GNFS.ZS)'
    },
    'İthalat': {
        'tanim': 'Dış dünyadan yerleşik kişi veya kurumlara satılan (ülkeye giren) mal ve hizmetlerin toplam değeri.',
        'birim': 'GSYİH İçindeki Payı (%)',
        'metodoloji': 'World Bank (NE.IMP.GNFS.ZS)'
    },
    'Tarım': ('Tarım Sektörü (% GSYİH)', 'Tarım, ormancılık ve balıkçılık sektörlerinin toplam katma değeridir.', 'World Bank (NV.AGR.TOTL.ZS)'),
    'Sanayi': ('Sanayi Sektörü (% GSYİH)', 'İmalat ve inşaat dahil tüm sanayi kollarının toplam katma değeridir.', 'World Bank (NV.IND.TOTL.ZS)'),
    'Hizmetler': ('Hizmetler Sektörü (% GSYİH)', 'Toptan, perakende, finans ve kamu hizmetlerinin katma değeridir.', 'World Bank (NV.SRV.TOTL.ZS)'),
    'HDI_UNDP': {
        'tanim': 'Ekonomik büyüme dogmasına karşı, insan merkezli bir kalkınma anlayışıyla ortalama yaşam süresi, eğitim erişimi ve insana yaraşır yaşam standardını ölçen bileşik endeks.',
        'birim': 'Endeks Skoru (0 - 1 Skalası)',
        'metodoloji': 'UNDP Human Development Report (hdr.undp.org)'
    },
    'IHDI': ('Eşitsizliğe Uyarlanmış İnsani Gelişme Endeksi (IHDI)', 'HDI\'nin gelir, sağlık ve eğitim eşitsizliği ile düzültilmiş versiyonu.', 'UNDP Human Development Report (hdr.undp.org)'),
    'PHDI': ('Gezegensel Baskılara Uyarlanmış İnsani Gelişme Endeksi (PHDI)', 'HDI\'nin karbon salınımı ve malzeme ayağı ile düzültilmiş hali.', 'UNDP Human Development Report (hdr.undp.org)'),
    'GII': {
        'tanim': 'Kadınların üreme sağlığı, siyasi/ekonomik güçlendirme ve işgücü piyasasına katılımları açısından maruz kaldıkları yapısal dezavantajları ölçen kompozit endekstir.',
        'birim': 'Endeks Değeri',
        'metodoloji': 'UNDP Human Development Report (hdr.undp.org)'
    },
    'GDI': ('Toplumsal Cinsiyet Gelişimi Endeksi (GDI)', 'Kadın ve erkek HDI değerlerinin oranıdır. 1.0=tam eşitlik.', 'UNDP Human Development Report (hdr.undp.org)'),
    'VDem_Score': ('V-Dem Liberal Demokrasi Endeksi', 'Siyasi katılım, hukukun üstünlüğü ve sivil özgürlükler üzerinden ülke demokrasisini ölçer.', 'V-Dem Institute (v-dem.net | v2x_libdem)'),
    'palma_ratio': {
        'tanim': 'Nüfusun en zengin %10\'luk kesiminin toplam gelirden aldığı payın, en yoksul %40\'lık kesimin aldığı paya oranı.',
        'birim': 'Oransal Katsayı',
        'metodoloji': 'WIID / SWIID Derived'
    },
    'WIID_Ratio': ('WIID S10/S1 Gelir Oranı', 'Nüfusun en zengin %10\'u ile en yoksul %10\'u arasındaki gelir payı oranıdır.', 'World Bank (SI.DST.10TH.10 / SI.DST.FRST.10)'),
    'Kamu Harcamaları': ('Kamu Harcamaları (% GSYİH)', 'Genel hükümet tüketim harcamalarının milli gelire oranıdır.', 'World Bank (NE.CON.GOVT.ZS)'),
    'Savunma Harcamaları': ('Savunma/Askeri Harcamalar (% GSYİH)', 'Silahlı kuvvetler için yapılan toplam kamu harcamasının milli gelire oranıdır.', 'World Bank (MS.MIL.XPND.GD.ZS)'),
    'Vergi Gelirleri': ('Vergi Gelirleri (% GSYİH)', 'Devletin zorunlu kıldığı vergi toplamının milli gelire oranıdır.', 'World Bank (GC.TAX.TOTL.GD.ZS)'),
    'Sosyal Refah': ('Sosyal Koruma Kapsamı (Nüfus %)', 'Herhangi bir sosyal koruma programından yararlanan nüfusun yüzdesidir.', 'Dünya Bankası ASPIRE Programı'),
    'Dış Borç': ('Dış Borç (% GSMH)', 'Yabancı alacaklılara olan toplam dış borç stokunun gayri safi milli hasılaya oranıdır.', 'World Bank (DT.DOD.DECT.GN.ZS)'),
    'IPI': ('Sanayi Üretim Endeksi (IPI)', 'Sanayi sektöründeki üretim hacminin değişimini ölçen endekstir.', 'IMF IFS / Yerel Hesaplama'),
    'PPI': ('Üretici Fiyat Endeksi (ÜFE / PPI)', 'Üreticilerin sattığı ürünlerin fiyat değişimini ölçen endekstir.', 'IMF IFS / Yerel Hesaplama'),
    'CDS': {
        'tanim': 'Bir ülkenin borç yükümlülüklerini temerrüde düşme riskine karşı sigortalamak için yatırımcının ödediği yıllık risk primi.',
        'birim': 'Baz Puan (bps) - 100 bps = %1',
        'metodoloji': 'Market Data (Mkt)'
    },
    'Kişi Başı Enerji (kWh)': {
        'tanim': 'Kişi başı yıllık birincil enerji tüketimi.',
        'birim': 'kWh',
        'metodoloji': 'Our World in Data (Energy)'
    },
    'Fosil Yakıt Payı (%)': {
        'tanim': 'Toplam elektrik üretiminde fosil yakıtların yüzdesi.',
        'birim': '%',
        'metodoloji': 'Our World in Data (Energy)'
    },
    'Yenilenebilir Payı (%)': {
        'tanim': 'Toplam elektrik üretiminde yenilenebilir kaynakların yüzdesi.',
        'birim': '%',
        'metodoloji': 'Our World in Data (Energy)'
    },
    'Karbon (Milyon Ton)': {
        'tanim': 'Fosil yakıt kullanımı kaynaklı yıllık toplam CO2 emisyonu.',
        'birim': 'Milyon Ton',
        'metodoloji': 'Our World in Data (CO2)'
    },
    'Kişi Başı Karbon (Ton)': {
        'tanim': 'Kişi başına düşen yıllık ortalama CO2 emisyonu.',
        'birim': 'Ton',
        'metodoloji': 'Our World in Data (CO2)'
    },
    'Enerji İthalatı Bağımlılığı': {
        'tanim': 'Toplam enerji kullanımında net enerji ithalatının yüzdesidir. Negatif değerler net ihracatçıyı gösterir.',
        'birim': '%',
        'metodoloji': 'World Bank (EG.IMP.CONS.ZS)'
    }
}


def get_metadata_value(meta_entry):
    """Dict veya tuple formatındaki metadata girişini normalize eder → (birim, tanim, kaynak) tuple'ı."""
    if isinstance(meta_entry, dict):
        birim = meta_entry.get('birim', '')
        tanim = meta_entry.get('tanim', '')
        kaynak = meta_entry.get('metodoloji', meta_entry.get('kod', ''))
        return (birim, tanim, kaynak)
    elif isinstance(meta_entry, tuple) and len(meta_entry) >= 3:
        return meta_entry
    elif isinstance(meta_entry, tuple) and len(meta_entry) == 2:
        return (meta_entry[0], meta_entry[1], '')
    return ('', '', '')
