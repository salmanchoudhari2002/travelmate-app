Map & Place Search UI

What I added
- A backend `/map/search` endpoint using OpenStreetMap Nominatim with optional Wikimedia thumbnails.
- A static Leaflet map UI served at `/map/ui` (static assets in `backend/app/static`).
- `frontend_simulator2.py` — simulator that searches for places and attaches `image_url` to local trips before syncing.
- A minimal Kivy frontend scaffold in `frontend_kivy/` with a place search screen and a new-trip screen that auto-fills image URL.

Run (local dev)
1) Activate your virtualenv and install requirements if not already installed:

```powershell
.\.venv\Scripts\activate; pip install -r requirements.txt
```

2) Start the backend (from project root):

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --app-dir (Get-Location).Path
```

3) Open the map UI in a browser:

http://127.0.0.1:8000/map/ui

4) Run the new simulator (it will save local trips with image_url when possible and sync):

```powershell
.\.venv\Scripts\python.exe frontend_simulator2.py
```

5) Run the Kivy GUI locally (desktop):

```powershell
.\.venv\Scripts\python.exe frontend_kivy\main.py
```

Notes
- Kivy on Windows requires additional build deps; if installation fails, run the simulator instead.
- Nominatim is rate-limited; for production use a commercial Places API with an API key (Google, Mapbox, Here).
