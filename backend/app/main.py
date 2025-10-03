from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from . import db
from .routes_trips import router as trips_router
from .auth import router as auth_router
from .export import router as export_router
from .routes_map import router as map_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import threading
import time
import os
from sqlmodel import Session
from .db import engine


app = FastAPI(title='Travel App API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def on_startup():
    # initialize DB and perform a tiny, safe migration for new columns
    db.init_db()
    # For SQLite, ensure 'image_url' and 'thumbnail' columns exist on Trip table
    try:
        with Session(engine) as session:
            # safe migration for SQLite: check table columns and add if missing
            try:
                res = session.exec("PRAGMA table_info('trip')").all()
                existing = {r[1] for r in res} if res else set()
            except Exception:
                existing = set()
            if 'image_url' not in existing:
                try:
                    session.exec("ALTER TABLE trip ADD COLUMN image_url TEXT")
                except Exception:
                    pass
            if 'thumbnail' not in existing:
                try:
                    session.exec("ALTER TABLE trip ADD COLUMN thumbnail TEXT")
                except Exception:
                    pass
            session.commit()
    except Exception:
        pass


app.include_router(auth_router, prefix='/auth')
app.include_router(trips_router, prefix='/trips')
app.include_router(export_router, prefix='/export')
app.include_router(map_router, prefix='/map')

# Serve static map UI
app.mount('/static', StaticFiles(directory='backend/app/static'), name='static')


@app.get('/map/ui')
def map_ui():
    return FileResponse('backend/app/static/index.html')


@app.get('/')
def root():
    return {'message': 'Travel App API running'}


IMAGE_TTL_SECONDS = 30 * 24 * 3600  # 30 days


@app.middleware('http')
async def cache_images_middleware(request: Request, call_next):
    resp = await call_next(request)
    try:
        path = request.url.path
        if path.startswith('/static/images/'):
            resp.headers['Cache-Control'] = 'public, max-age=604800, immutable'
    except Exception:
        pass
    return resp


def _cleanup_worker(static_dir: str):
    while True:
        try:
            now = time.time()
            for root, dirs, files in os.walk(static_dir):
                for name in files:
                    p = os.path.join(root, name)
                    try:
                        mtime = os.path.getmtime(p)
                        if now - mtime > IMAGE_TTL_SECONDS:
                            os.remove(p)
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(24 * 3600)


@app.on_event('startup')
def start_cleanup_thread():
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    t = threading.Thread(target=_cleanup_worker, args=(static_dir,), daemon=True)
    t.start()
