from flask import Blueprint, request
import orjson
from bustrackr_server.utils import orjson_default
from bustrackr_server.services.stops_service import (
    process_coordinates,
    is_area_too_large,
    find_stops,
    format_stops_response
)

stops_bp = Blueprint('stops', __name__)

@stops_bp.route('/stops', methods=['POST'])
def get_stops():
    try:
        req = request.get_json()
        validate_request(req)
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    try:
        lat_0, lon_0, lat_1, lon_1 = process_coordinates(req)
    except ValueError:
        return orjson.dumps({'status': 'error', 'message': 'Invalid values'}), 400
    
    if is_area_too_large(lat_0, lon_0, lat_1, lon_1):
        return orjson.dumps({'status': 'error', 'message': 'Requested area is too large'}), 422
    
    stops = find_stops(lat_0, lon_0, lat_1, lon_1)
    response = format_stops_response(stops)
    return orjson.dumps(response, default=orjson_default), 200

def validate_request(req: dict) -> None:
    if req is None:
        raise TypeError("Content-Type is incorrect, JSON is malformed, or empty")
    required_fields = {'lat_0', 'lon_0', 'lat_1', 'lon_1'}
    if not required_fields.issubset(req):
        raise ValueError("Missing required fields")