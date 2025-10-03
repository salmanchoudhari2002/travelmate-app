import requests, json

r = requests.get('http://127.0.0.1:8000/map/search', params={'query':'Taj Mahal','limit':1}, timeout=15)
print('status', r.status_code)
js = r.json()
print(json.dumps(js, indent=2))
if js.get('results'):
    t = js['results'][0]
    print('thumbnail field:', t.get('thumbnail'))
    thumb = t.get('thumbnail')
    if thumb and thumb.startswith('/static'):
        url = 'http://127.0.0.1:8000' + thumb
        h = requests.head(url)
        print('HEAD', h.status_code)
        for k,v in h.headers.items():
            if k.lower() in ('cache-control','content-type','content-length'):
                print(k+':', v)
