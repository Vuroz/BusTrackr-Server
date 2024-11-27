from bustrackr_server import app, db
from bustrackr_server.models import Stop, Quay
from sqlalchemy import and_, or_, func, select
from flask import request
import json

@app.route('/')
def index():
    '''Handler for index the index (`/`) route'''
    return '<p>Hello, World!</p>'

@app.route('/api/stops', methods=['POST'])
def get_stops():
    '''Handler for the `/api/stops` route'''
    try:
        req = request.get_json()
    except:
        return 'Invalid JSON', 400
    if req is None:
        return 'Invalid JSON', 400
    if 'lat_0' not in req or 'lon_0' not in req or 'lat_1' not in req or 'lon_1' not in req:
        return 'Missing required fields', 400
    
    try:
        lat_0 = float(req['lat_0']) + 0.01
        lon_0 = float(req['lon_0']) - 0.01
        lat_1 = float(req['lat_1']) - 0.01
        lon_1 = float(req['lon_1']) + 0.01
    except ValueError:
        return 'Invalid values', 400

    lat_len = lat_0 - lat_1
    lon_len = lon_1 - lon_0
    area = lat_len * lon_len
    # Magic number, 0.025 is the maximum area allowed (completely arbitratory but somewhat reasonable)
    if area > 0.025:
        return 'Area too large', 400
    
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

    return json.dumps(json_response, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 200