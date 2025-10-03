import requests

BASE = 'http://127.0.0.1:8000'
q = 'Taj Mahal'
print('Querying /map/search for', q)
try:
    r = requests.get(f'{BASE}/map/search', params={'query': q, 'limit': 1}, timeout=15)
    print('status', r.status_code)
    data = r.json().get('results', [])
    if data:
        print('result keys:', list(data[0].keys()))
        print('thumbnail:', data[0].get('thumbnail'))
    else:
        print('no results returned')
except Exception as e:
    print('error', e)
