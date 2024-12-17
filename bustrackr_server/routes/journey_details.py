from flask import Blueprint, request
import orjson
from bustrackr_server.utils import orjson_default
from bustrackr_server.services.journey_details_service import (
    is_info_availible,
    get_journey_info,
    get_vehicle_info,
    format_journey_details_response
)

journey_details_bp = Blueprint('journey_details', __name__)

@journey_details_bp.route('/journey_details', methods=['POST'])
def get_journey_details():
    try:
        req = request.get_json()
        validate_request(req)
    except ValueError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 400
    except TypeError as e:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 415
    except:
        return orjson.dumps({'status': 'error', 'message': str(e)}), 500

    journey_availible, vehicle_availible = is_info_availible(req)

    journey_data = None
    if journey_availible:
        journey_data = get_journey_info(req)

    vehicle_data = None
    if vehicle_availible:
        vehicle_data = get_vehicle_info(req)

    response = format_journey_details_response(journey_data, vehicle_data)
    return orjson.dumps(response, default=orjson_default), 200





def validate_request(req: dict) -> None:
    if req is None:
        raise TypeError("Content-Type is incorrect, JSON is malformed, or empty")
    required_fields = {'service_journey_id', 'vehicle_id'}
    if not required_fields.issubset(req):
        raise ValueError("Missing required fields")