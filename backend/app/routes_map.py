from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import os
import hashlib
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

router = APIRouter()

NOMINATIM_URL = os.environ.get('NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search')
STATIC_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
THUMB_DIR = os.path.join(STATIC_IMAGES_DIR, 'thumbnails')
os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)


def _download_and_make_thumbnail(thumb_src: str, fname: str, local_path: str, thumb_name: str, thumb_path: str):
    """Download the remote thumbnail and save original + generated thumbnail to disk."""
    headers = {'User-Agent': 'TravelApp/1.0 (+https://example.com)'}
    try:
        ir = requests.get(thumb_src, headers=headers, timeout=15)
        if ir.status_code == 200:
            # save original
            with open(local_path, 'wb') as f:
                f.write(ir.content)
            # create thumbnail
            try:
                img = Image.open(BytesIO(ir.content))
                img.thumbnail((320, 240))
                img.save(thumb_path)
            except Exception:
                # cleanup partial thumbnail if any
                if os.path.exists(thumb_path):
                    try:
                        os.remove(thumb_path)
                    except Exception:
                        pass
    except Exception:
        # swallow errors; background task should not crash the server
        return


@router.get('/search')
def place_search(query: str = Query(..., min_length=1), limit: int = 10, background_tasks: BackgroundTasks = None):
    params = {
        'q': query,
        'format': 'jsonv2',
        'limit': limit,
        'addressdetails': 1,
        'extratags': 1,
        'namedetails': 1,
    }
    headers = {'User-Agent': 'TravelApp/1.0 (+https://example.com)'}
    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f'Nominatim error: {e}')

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail='Nominatim returned error')

    data = r.json()
    results = []
    for item in data:
        name = item.get('namedetails', {}).get('name') or item.get('display_name')
        lat = float(item.get('lat')) if item.get('lat') else None
        lon = float(item.get('lon')) if item.get('lon') else None
        osm_type = item.get('osm_type')
        osm_id = item.get('osm_id')
        osm_letter = {'node': 'n', 'way': 'w', 'relation': 'r'}.get(osm_type, '')
        osm_url = f'https://www.openstreetmap.org/{osm_letter}{osm_id}' if osm_id else None
        icon = item.get('icon')
        result = {
            'name': name,
            'display_name': item.get('display_name'),
            'lat': lat,
            'lon': lon,
            'type': item.get('type'),
            'class': item.get('class'),
            'boundingbox': item.get('boundingbox'),
            'icon': icon,
            'osm_url': osm_url,
            'extratags': item.get('extratags', {}),
            'image': None,
        }

        # if wikipedia tag present, fetch summary to get thumbnail; cache image locally
        extratags = item.get('extratags', {}) or {}
        wiki_tag = extratags.get('wikipedia')
        if wiki_tag:
            try:
                lang, page = wiki_tag.split(':', 1)
                page = page.replace(' ', '_')
                summary_url = f'https://{lang}.wikipedia.org/api/rest_v1/page/summary/{page}'
                wr = requests.get(summary_url, headers=headers, timeout=6)
                if wr.status_code == 200:
                    js = wr.json()
                    thumb = js.get('thumbnail', {})
                    thumb_src = thumb.get('source')
                    if thumb_src:
                        # cache by URL hash and preserve extension
                        try:
                            parsed = urlparse(thumb_src)
                            ext = os.path.splitext(parsed.path)[1] or '.jpg'
                            h = hashlib.sha1(thumb_src.encode('utf8')).hexdigest()
                            fname = f"{h}{ext}"
                            local_path = os.path.join(STATIC_IMAGES_DIR, fname)
                            thumb_name = f"{h}_thumb{ext}"
                            thumb_path = os.path.join(THUMB_DIR, thumb_name)

                            # if both exist, return local references immediately
                            if os.path.exists(local_path) and os.path.exists(thumb_path):
                                result['image'] = f"/static/images/{fname}"
                                result['thumbnail'] = f"/static/images/thumbnails/{thumb_name}"
                            else:
                                # schedule background download/thumbnail generation
                                # return remote image for immediate display; thumbnail will be available later
                                result['image'] = thumb_src
                                result['thumbnail'] = None
                                # schedule background task to create cached files
                                # BackgroundTasks must be supplied by the route — we will add it in the signature
                                if background_tasks is not None:
                                    background_tasks.add_task(_download_and_make_thumbnail, thumb_src, fname, local_path, thumb_name, thumb_path)
                        except Exception:
                            result['image'] = thumb_src
            except Exception:
                pass

        results.append(result)

    return JSONResponse(content={'results': results})

