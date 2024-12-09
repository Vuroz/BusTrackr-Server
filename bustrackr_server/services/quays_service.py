from typing import List, Tuple
from sqlalchemy import select, and_
from bustrackr_server import db
from bustrackr_server.models import Quay, Stop

def process_coordinates(req: dict) -> Tuple[float, float, float, float]:
    """Process and slightly adjust input coordinates."""
    lat_0 = float(req['lat_0']) + 0.01
    lon_0 = float(req['lon_0']) - 0.01
    lat_1 = float(req['lat_1']) - 0.01
    lon_1 = float(req['lon_1']) + 0.01
    return lat_0, lon_0, lat_1, lon_1

def is_area_too_large(lat_0: float, lon_0: float, lat_1: float, lon_1: float) -> bool:
    """Check if the reqested area is too large."""
    lat_len = lat_0 - lat_1
    lon_len = lon_1 - lon_0
    area = lat_len * lon_len
    return area > 0.025

def find_quays(lat_0: float, lon_0: float, lat_1: float, lon_1: float) -> List:
    """Fetch quays from the database based on input coordinates"""
    find_quays_query = select(
        Quay.id.label('id'),
        Quay.stop_id.label('stop_id'),
        Quay.public_code.label('code'),
        Quay.latitude.label('lat'),
        Quay.longitude.label('lon'),
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
    return db.session.execute(find_quays_query).fetchall()

def format_quays_response(quays_in_area: List) -> dict:
    """Format the database results into a structured dict (ready to be parsed to JSON)"""
    return {
            'status': 'ok',
            'type': 'quays',
            'list': [
                {
                    'id': str(quay.id),
                    'stop_id': str(quay.stop_id),
                    'code': quay.code,
                    'name': quay.name,
                    'location': {'lat': quay.lat, 'lon': quay.lon}
                }
                for quay in quays_in_area
            ]
    }