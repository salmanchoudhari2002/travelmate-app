import requests

def run():
    base = 'http://127.0.0.1:8000'
    try:
        r = requests.get(f'{base}/map/search', params={'query':'Taj Mahal','limit':3}, timeout=10)
        print('/map/search status', r.status_code)
        if r.status_code==200:
            res = r.json()
            print('results count', len(res.get('results',[])))
            if res.get('results'):
                print('first display_name:', res['results'][0].get('display_name','')[:200])
    except Exception as e:
        print('search error', e)
    try:
        r2 = requests.get(f'{base}/map/ui', timeout=10)
        print('/map/ui status', r2.status_code)
        print('ui length', len(r2.text) if r2.status_code==200 else 'n/a')
    except Exception as e:
        print('ui error', e)

if __name__ == '__main__':
    run()
