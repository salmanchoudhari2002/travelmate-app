from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import db
from .routes_trips import router as trips_router
from .auth import router as auth_router
from .export import router as export_router
from .routes_map import router as map_router

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
    db.init_db()

app.include_router(auth_router, prefix='/auth')
app.include_router(trips_router, prefix='/trips')
app.include_router(export_router, prefix='/export')
app.include_router(map_router, prefix='/map')

@app.get('/')
def root():
    return {'message': 'Travel App API running'}
