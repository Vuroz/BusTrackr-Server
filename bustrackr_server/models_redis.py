from redis_om import HashModel, Field
from datetime import datetime
from bustrackr_server import redis_client

# This file is similar to the models.py (for the static data) except for the realtime data

class VehicleLive(HashModel):
    service_journey_id: int = Field(index=True)
    vehicle_id: int = Field(index=True)
    bearing: float
    velocity: int
    longitude: float = Field(index=True)
    latitude: float = Field(index=True)
    timestamp: datetime

    class Meta:
        primary_key = ('service_journey_id', 'vehicle_id')
        database = redis_client