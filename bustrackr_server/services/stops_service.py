from typing import List, Tuple
from sqlalchemy import select, and_
from bustrackr_server import db
from bustrackr_server.models import Stop, AlternativeName

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
    return area > 0.125

def find_stops(lat_0: float, lon_0: float, lat_1: float, lon_1: float) -> List:
    """Fetch stops from the database based on input coordinates"""
    find_stops_query = select(
        Stop.id.label('id'),
        Stop.stop_group_id.label('group_id'),
        Stop.name.label('name'),
        Stop.latitude.label('lat'),
        Stop.longitude.label('lon'),
        AlternativeName.abbreviation.label('abb')
    ).join_from(
        Stop, AlternativeName,
        Stop.id == AlternativeName.stop_id,
        isouter=True
    ).where(
        and_(
            Stop.transport_mode == 'bus',
            Stop.latitude <= lat_0,
            Stop.latitude >= lat_1,
            Stop.longitude >= lon_0,
            Stop.longitude <= lon_1
        )
    )
    return db.session.execute(find_stops_query).fetchall()

def format_stops_response(stops_in_area: List) -> dict:
    """Format the database results into a structured dict (ready to be parsed to JSON)"""
    return {
            'status': 'ok',
            'type': 'stops',
            'list': [
                {
                    'id': stop.id,
                    'group_id': stop.group_id or None,
                    'name': stop.name,
                    'abb': stop.abb or None,
                    'location': {'lat': stop.lat, 'lon': stop.lon}
                }
                for stop in stops_in_area
            ]
    }