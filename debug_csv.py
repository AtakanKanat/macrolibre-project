import pandas as pd

# 0.4.0 - Latin-1 deneyebiliriz
try:
    df1 = pd.read_csv('c:/Users/pc/Desktop/2antigravity/0.4.0/social_indicators.csv', encoding='latin-1')
    print('=== 0.4.0 (2MB) ===')
    print('Sutunlar:', df1.columns.tolist())
    print('Satirlar:', df1.shape[0])
    print(df1.head(2).to_string())
except Exception as e:
    print('0.4.0 HATA:', e)

print()

# HDI verileri
try:
    df2 = pd.read_csv('c:/Users/pc/Desktop/2antigravity/HDI verileri/social_indicators.csv', encoding='utf-8')
    print('=== HDI verileri (107KB) ===')
    print('Sutunlar:', df2.columns.tolist())
    print('Satirlar:', df2.shape[0])
    print(df2.head(2).to_string())
except Exception as e:
    try:
        df2 = pd.read_csv('c:/Users/pc/Desktop/2antigravity/HDI verileri/social_indicators.csv', encoding='latin-1')
        print('=== HDI verileri (latin-1) ===')
        print('Sutunlar:', df2.columns.tolist())
        print('Satirlar:', df2.shape[0])
        print(df2.head(2).to_string())
    except Exception as e2:
        print('HDI HATA:', e2)
