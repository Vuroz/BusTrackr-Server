from typing import List, Tuple
from bustrackr_server.models_redis import VehicleLive

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

def find_live_buses(lat_0: float, lon_0: float, lat_1: float, lon_1: float) -> List:
    """Fetch live buses from redis based on input coordinates"""
    buses = VehicleLive.find(
        (VehicleLive.latitude > lat_1) & (VehicleLive.latitude < lat_0) &  
        (VehicleLive.longitude > lon_0) & (VehicleLive.longitude < lon_1)
    ).all() # The resulting query is not optimized, but it works
    return buses

def format_live_buses_response(live_buses_in_area: List) -> dict:
    """Format the redis results into a structured dict (ready to be parsed to JSON)"""
    latest_entries = {}
    
    # Filter to only keep the latest entry of every bus
    for bus in live_buses_in_area:
        key = (bus.service_journey_id, bus.vehicle_id)
        if key not in latest_entries or bus.timestamp > latest_entries[key].timestamp:
            latest_entries[key] = bus

    live_buses_in_area = list(latest_entries.values())
    
    return {
        'status': 'ok',
        'type': 'live_buses',
        'list': [
            {
                'service_journey_id': str(bus.service_journey_id),
                'vehicle_id': str(bus.vehicle_id),
                'time': bus.timestamp,
                'bearing': bus.bearing,
                'velocity': bus.velocity,
                'location': {'lat': bus.latitude, 'lon': bus.longitude}
            }
            for bus in live_buses_in_area
        ]
    }