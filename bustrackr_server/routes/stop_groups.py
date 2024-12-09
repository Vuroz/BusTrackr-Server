from flask import Blueprint, request
import orjson
from bustrackr_server.utils import orjson_default
from bustrackr_server.services.stop_groups_service import (
    process_coordinates,
    is_area_too_large,
    find_groups_coords,
    find_groups_list,
    format_groups_response
)

groups_bp = Blueprint('stop_groups', __name__)

@groups_bp.route('/stop_groups', methods=['POST'])
def stop_groups():
    try:
        req = request.get_json()
        validate_request(req)
        req_type = req['type']
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': 'Internal server error'}), 500
    
    if req_type == 'list':
        groups = find_groups_list(req['list'])
    elif req_type == 'coordinates':
        lat_0, lon_0, lat_1, lon_1 = process_coordinates(req)
        if is_area_too_large(lat_0, lon_0, lat_1, lon_1):
            return orjson.dumps({'status': 'error', 'message': 'Area is too large'}), 400
        groups = find_groups_coords(lat_0, lon_0, lat_1, lon_1)
    else:
        return orjson.dumps({'status': 'error', 'message': 'Invalid request type'}), 400
    
    response = format_groups_response(groups)
    return orjson.dumps(response, default=orjson_default), 200
    

def validate_request(req: dict) -> None:
    if req is None:
        raise TypeError("Content-Type is incorrect, JSON is malformed, or empty")
    if 'type' not in req:
        raise ValueError("Missing required field: 'type'")
    if req['type'] == 'list':
        if 'list' not in req:
            raise ValueError("Missing required field: 'list'")
    elif req['type'] == 'coordinates':
        required_fields = {'lat_0', 'lon_0', 'lat_1', 'lon_1'}
        if not required_fields.issubset(req):
            raise ValueError("Missing required fields")
    else:
        raise ValueError("Invalid 'type' value")