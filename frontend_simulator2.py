"""Simulator v2: uses /map/search to attach image_url to local trips, then syncs to backend."""
import requests
import json
import time
import os

BASE = os.environ.get('TRAVEL_BACKEND_URL', 'http://127.0.0.1:8000')
LOCAL_STORE = 'local_store.json'


def signup(email, password):
    r = requests.post(f"{BASE}/auth/signup", json={'email': email, 'password': password})
    r.raise_for_status()
    return r.json()['access_token']


def login(email, password):
    r = requests.post(f"{BASE}/auth/token", data={'username': email, 'password': password})
    r.raise_for_status()
    return r.json()['access_token']


def read_local():
    if not os.path.exists(LOCAL_STORE):
        return []
    with open(LOCAL_STORE, 'r', encoding='utf8') as f:
        return json.load(f).get('items', [])


def save_local_trip(destination, mode, expenses):
    store = {'items': []}
    if os.path.exists(LOCAL_STORE):
        with open(LOCAL_STORE, 'r', encoding='utf8') as f:
            try:
                store = json.load(f)
            except Exception:
                store = {'items': []}

    # try to find an image for the destination via backend map search
    image_url = None
    try:
        r = requests.get(f"{BASE}/map/search", params={'query': destination, 'limit': 1}, timeout=6)
        if r.status_code == 200:
            res = r.json().get('results', [])
            if res and res[0].get('image'):
                image_url = res[0].get('image')
    except Exception:
        image_url = None

    store.setdefault('items', []).append({
        'destination': destination,
        'mode': mode,
        'expenses': expenses,
        'synced': False,
        'image_url': image_url,
    })

    with open(LOCAL_STORE, 'w', encoding='utf8') as f:
        json.dump(store, f, indent=2)

    print(f"Saved local trip: {destination} (image: {bool(image_url)})")


def sync(token):
    unsynced = [t for t in read_local() if not t.get('synced')]
    if not unsynced:
        print('No unsynced trips to sync')
        return
    headers = {'Authorization': f'Bearer {token}'}
    # remove local-only keys
    payload = []
    for t in unsynced:
        cleaned = {k: v for k, v in t.items() if k in ('start_lat','start_lng','destination','mode','start_date','end_date','expenses','purpose','notes','image_url')}
        payload.append(cleaned)
    r = requests.post(f"{BASE}/trips/sync", json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    print('Sync response:', r.json())
    # mark local as synced
    items = read_local()
    for it in items:
        it['synced'] = True
    with open(LOCAL_STORE, 'w', encoding='utf8') as f:
        json.dump({'items': items}, f, indent=2)


def list_remote(token):
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"{BASE}/trips/", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    t = time.strftime('%Y%m%d%H%M%S')
    email = f'sim2_{t}@example.com'
    pw = 'SimPass123!'
    print('BASE:', BASE)
    print('Step 1: signup')
    try:
        token = signup(email, pw)
        print('Signup token len:', len(token))
    except Exception as e:
        print('Signup failed:', e)
        print('Attempting login instead...')
        try:
            token = login(email, pw)
            print('Login token len:', len(token))
        except Exception as e2:
            print('Login also failed:', e2)
            raise SystemExit(1)

    print('Step 2: save two local trips with images (if available)')
    save_local_trip('Taj Mahal', 'Sightseeing', 20.0)
    save_local_trip('Eiffel Tower', 'Sightseeing', 15.0)

    print('Local store now:')
    print(json.dumps(read_local(), indent=2))

    print('Step 3: sync to backend')
    sync(token)

    print('Step 4: list remote trips')
    remote = list_remote(token)
    print(json.dumps(remote, indent=2))

    print('Done. Open http://127.0.0.1:8000/map/ui to try the map UI.')
