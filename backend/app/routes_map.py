from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/nearby')
def nearby_suggestions(lat: float, lng: float):
    suggestions = [
        {'name': 'Central Park', 'lat': lat + 0.01, 'lng': lng + 0.01, 'type': 'park'},
        {'name': 'City Museum', 'lat': lat + 0.02, 'lng': lng - 0.01, 'type': 'museum'},
    ]
    return JSONResponse(content={'results': suggestions})
