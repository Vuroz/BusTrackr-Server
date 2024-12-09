from typing import List, Tuple
from sqlalchemy import select, and_, any_
# from sqlalchemy.dialects.postgresql import array
from bustrackr_server import db
from bustrackr_server.models import StopGroup

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
    return area > 0.325

def find_groups_coords(lat_0: float, lon_0: float, lat_1: float, lon_1: float) -> List:
    """Fetch stop groups from the database based on input coordinates"""
    find_groups_query = select(
        StopGroup.id.label('id'),
        StopGroup.name.label('name'),
        StopGroup.description.label('desc'),
        StopGroup.latitude.label('lat'),
        StopGroup.longitude.label('lon')
    ).where(
        and_(
            StopGroup.latitude <= lat_0,
            StopGroup.latitude >= lat_1,
            StopGroup.longitude >= lon_0,
            StopGroup.longitude <= lon_1
        )
    )
    return db.session.execute(find_groups_query).fetchall()

def find_groups_list(ids: List) -> List:
    """Fetch stop groups from the database based on list of ids"""
    find_groups_query = select(
        StopGroup.id.label('id'),
        StopGroup.name.label('name'),
        StopGroup.description.label('desc'),
        StopGroup.latitude.label('lat'),
        StopGroup.longitude.label('lon')
    ).where(
        StopGroup.id == any_(ids)
    )
    return db.session.execute(find_groups_query).fetchall()

def format_groups_response(groups_in_area: List) -> dict:
    """Format the database results into a structured dict (ready to be parsed to JSON)"""
    return {
            'status': 'ok',
            'type': 'stop_groups',
            'list': [
                {
                    'id': str(group.id),
                    'name': group.name,
                    'desc': group.desc or None,
                    'location': {'lat': group.lat, 'lon': group.lon}
                }
                for group in groups_in_area
            ]
    }