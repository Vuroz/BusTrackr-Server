from typing import List, Tuple
from sqlalchemy import select, Row
from bustrackr_server import db
from bustrackr_server.models import (
    Journey,
    Vehicle,
    JourneyPattern,
    Route,
    Line,
    PointOnRoute,
    PassengerStop,
    Quay,
    Stop,
    VehicleType,
    Authority
)

def is_info_availible(req: dict) -> Tuple[bool, bool]:
    find_journey_query = select(
        Journey.id
    ).select_from(Journey).where(
        Journey.id == int(req['service_journey_id'])
    )

    find_vehicle_query = select(
        Vehicle.id
    ).select_from(Vehicle).where(
        Vehicle.id == int(req['vehicle_id'])
    )

    journey_result = db.session.execute(find_journey_query).one_or_none()
    vehicle_result = db.session.execute(find_vehicle_query).one_or_none()

    journey_exists = True if journey_result else False
    vehicle_exists = True if vehicle_result else False

    return (journey_exists, vehicle_exists)

def get_journey_info(req: dict) -> List:
    """Fetches relevant information regarding the journey from the database"""
    journey_info_query = select(
        Journey.id.label('journey_id'),
        Line.public_code.label('line'),
        Route.name.label('destination'),
        PointOnRoute.order.label('stop_nr'),
        Stop.id.label('stop_id'),
        Stop.name.label('stop_name')
    ).join_from(
        Journey, JourneyPattern,
        Journey.journey_pattern_id == JourneyPattern.id
    ).join(
        Route,
        JourneyPattern.route_id == Route.id
    ).join(
        Line,
        Route.line_id == Line.id
    ).join(
        PointOnRoute,
        Route.id == PointOnRoute.route_id
    ).join(
        PassengerStop,
        PointOnRoute.scheduled_stop_point_id == PassengerStop.scheduled_stop_point_id
    ).join(
        Quay,
        PassengerStop.quay_id == Quay.id
    ).join(
        Stop,
        Quay.stop_id == Stop.id
    ).where(
        Journey.id == int(req['service_journey_id'])
    ).order_by(
        PointOnRoute.order
    )

    return db.session.execute(journey_info_query).fetchall()

def get_vehicle_info(req: dict) -> Row | None:
    vehicle_info_query = select(
        Vehicle.id.label('id'),
        VehicleType.manufacturer.label('manufacturer'),
        VehicleType.model_year.label('model_year'),
        VehicleType.capacity_seated.label('seated'),
        VehicleType.capacity_standing.label('standing'),
        VehicleType.capacity_pushchair.label('pushchair'),
        VehicleType.capacity_wheelchair.label('wheelchair'),
        Authority.name.label('operator')
    ).join_from(
        Vehicle, VehicleType,
        Vehicle.vehicle_type_id == VehicleType.id
    ).join(
        Authority,
        Vehicle.operator_id == Authority.id
    ).where(
        Vehicle.id == int(req['vehicle_id'])
    )

    return db.session.execute(vehicle_info_query).first()

def format_journey_details_response(journey_data: List | None, vehicle_data: Row | None) -> dict:
    """Format the database results into a structured dict (ready to be parsed to JSON)"""
    obj = {
        'status': 'ok',
        'type': 'journey_details',
    }

    if journey_data:
        obj['journey_id'] = str(journey_data[0].journey_id)
        obj['line'] = str(journey_data[0].line)
        obj['destination'] = str(journey_data[0].destination)
        obj['stops'] = [
            {
                'id': str(stop.stop_id),
                'nr': str(stop.stop_nr),
                'name': str(stop.stop_name),
            }
            for stop in journey_data
        ]


    if vehicle_data:
        obj['vehicle_id'] = str(vehicle_data.id)
        obj['manufacturer'] = vehicle_data.manufacturer
        obj['model_year'] = vehicle_data.model_year
        obj['seated'] = vehicle_data.seated
        obj['standing'] = vehicle_data.standing
        obj['pushchair'] = vehicle_data.pushchair
        obj['wheelchair'] = vehicle_data.wheelchair
        obj['operator'] = vehicle_data.operator

    return obj