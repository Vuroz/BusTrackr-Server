from bustrackr_server import app, db
from bustrackr_server.models import Stop, Quay
from bustrackr_server.utils import orjson_default
from sqlalchemy import and_, or_, func, select
from flask import request
import orjson

@app.route('/')
def index():
    '''Handler for index the index (`/`) route'''
    return '<p>Hello, World!</p>'

@app.route('/api/quays', methods=['POST'])
def get_quays():
    '''Handler for the `/api/quays` route'''
    try:
        req = request.get_json()
        if req is None:
            raise ValueError('Empty JSON')
    except:
        return orjson.dumps({
            'status': 'error',
            'message': 'Content-Type is incorrect, JSON is malformed, or empty'
        }), 415 # Unsupported Media Type (either JSON parsing failed or Content-Type was not set to application/json)
    if 'lat_0' not in req or 'lon_0' not in req or 'lat_1' not in req or 'lon_1' not in req:
        return orjson.dumps({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400
    
    try:
        lat_0 = float(req['lat_0']) + 0.01
        lon_0 = float(req['lon_0']) - 0.01
        lat_1 = float(req['lat_1']) - 0.01
        lon_1 = float(req['lon_1']) + 0.01
    except ValueError:
        return orjson.dumps({
            'status': 'error',
            'message': 'Invalid values'
        }), 400

    lat_len = lat_0 - lat_1
    lon_len = lon_1 - lon_0
    area = lat_len * lon_len
    # Magic number, 0.025 is the maximum area allowed (completely arbitratory but somewhat reasonable)
    if area > 0.025:
        return orjson.dumps({
            'status': 'error',
            'message': 'Requested area is too large'
        }), 422 # Unprocessable Content
    
    find_quays_query = select(
        Quay.stop_id.label('stop_id'),
        Quay.public_code.label('code'),
        Quay.latitude.label('latitude'),
        Quay.longitude.label('longitude'),
        Stop.name.label('name')
    ).join_from(
        Quay, Stop,
        Quay.stop_id == Stop.id
    ).where(
        and_(
            Stop.transport_mode == 'bus',
            Quay.latitude <= lat_0,
            Quay.latitude >= lat_1,
            Quay.longitude >= lon_0,
            Quay.longitude <= lon_1
        )
    )

    quays_in_area = db.session.execute(find_quays_query).fetchall()

    json_response = {
        'status': 'ok',
        'type': 'quays',
        'list': [],
    }

    for quay in quays_in_area:
        json_response['list'].append({
            'stop_id': quay.stop_id,
            'code': quay.code,
            'name': quay.name,
            'location': {
                'lat': quay.latitude,
                'lon': quay.longitude
            }
        })

    return (
        orjson.dumps(
            json_response,
            default=orjson_default
        ),
        200
    )