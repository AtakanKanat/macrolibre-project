import urllib.request, json

URLS_TO_TRY = [
    'https://raw.githubusercontent.com/factbook/factbook.json/master/east-asia-pacific/tw.json',
    'https://raw.githubusercontent.com/factbook/factbook.json/master/taiwan/tw.json',
    'https://raw.githubusercontent.com/factbook/factbook.json/master/asia/tw.json',
]

for url in URLS_TO_TRY:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        print('FOUND AT:', url)
        econ = data.get('Economy', {})
        print('Economy keys:', list(econ.keys())[:5])
        # GDP verisi ara
        for k, v in econ.items():
            if 'GDP' in k.upper() and isinstance(v, dict):
                print(f'  {k}:', json.dumps(v, indent=2)[:400])
                break
        break
    except Exception as e:
        print(f'{url}: {e}')
