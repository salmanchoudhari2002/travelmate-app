import requests, json, os, time
BASE = os.environ.get('TRAVEL_BACKEND_URL', 'http://127.0.0.1:8000')
email = f"debug_{int(time.time())}@example.com"
pw = 'DebugPass123!'
print('Using BASE:', BASE)
# signup
r = requests.post(f"{BASE}/auth/signup", json={'email': email, 'password': pw})
print('signup status', r.status_code)
print(r.text)
if r.status_code != 200:
    print('Signup failed, attempting login')
    r = requests.post(f"{BASE}/auth/token", data={'username': email, 'password': pw})
    print('login status', r.status_code)
    print(r.text)
    r.raise_for_status()
token = r.json()['access_token']
print('token len', len(token))
# read local store
LOCAL_STORE = 'local_store.json'
if not os.path.exists(LOCAL_STORE):
    print('No local store file found')
    exit(0)
with open(LOCAL_STORE, 'r', encoding='utf8') as f:
    items = json.load(f).get('items', [])
unsynced = [t for t in items if not t.get('synced')]
print('unsynced items:', json.dumps(unsynced, indent=2))
# prepare payload
payload = []
for t in unsynced:
    cleaned = {k: v for k, v in t.items() if k in ('start_lat','start_lng','destination','mode','start_date','end_date','expenses','purpose','notes')}
    payload.append(cleaned)
print('payload to send:', json.dumps(payload, indent=2))
headers = {'Authorization': f'Bearer {token}'}
r = requests.post(f"{BASE}/trips/sync", json=payload, headers=headers)
print('response status', r.status_code)
try:
    print('response json:', json.dumps(r.json(), indent=2))
except Exception:
    print('response text:', r.text)
    r.raise_for_status()
print('done')
