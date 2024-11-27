from sqlalchemy.dialects.sqlite import INTEGER, TEXT, REAL
from bustrackr_server import db

class Authority(db.Model):
    '''Representation of an authority in the database'''
    __tablename__ = 'authority'
    id = db.Column(INTEGER, name='id', primary_key=True)
    from_datetime  = db.Column(TEXT   , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TEXT   , name='to_datetime'   , nullable=True )
    name           = db.Column(TEXT   , name='name'          , nullable=False)
    name_legal     = db.Column(TEXT   , name='name_legal'    , nullable=False)
    private_code   = db.Column(INTEGER, name='private_code'  , nullable=False)
    company_number = db.Column(TEXT   , name='company_number', nullable=True )
    type           = db.Column(TEXT   , name='type'          , nullable=False)
        
    stops    = db.relationship('Stop',
                               primaryjoin='Authority.id == Stop.authority_id',
                               back_populates='authority',
                               uselist=True)
    vehicles = db.relationship('Vehicle',
                               primaryjoin='Authority.id == Vehicle.operator_id',
                               back_populates='operator',
                               uselist=True)
    network  = db.relationship('Network',
                               primaryjoin='Authority.id == Network.authority_id',
                               back_populates='authority',
                               uselist=False)
    journeys = db.relationship('Journey',
                               primaryjoin='Authority.id == Journey.operator_id',
                               back_populates='operator',
                               uselist=True)

class VehicleType(db.Model):
    '''Representation of a vehicle type in the database'''
    __tablename__ = 'vehicle_type'
    id = db.Column(INTEGER, name='id', primary_key=True)
    type                = db.Column(TEXT   , name='type'               , nullable=False)
    manufacturer        = db.Column(TEXT   , name='manufacturer'       , nullable=True ) # Not all vehicles have a manufacturer (for some reason?)
    model_year          = db.Column(INTEGER, name='model_year'         , nullable=True ) # I think all vehicles have a model year, but leave it as nullable just in case
    fuel_type           = db.Column(TEXT   , name='fuel_type'          , nullable=True ) # Not all vehicles have a fuel type (for some reason?)
    capacity_seated     = db.Column(INTEGER, name='capacity_seated'    , nullable=False)
    capacity_standing   = db.Column(INTEGER, name='capacity_standing'  , nullable=False)
    capacity_pushchair  = db.Column(INTEGER, name='capacity_pushchair' , nullable=False)
    capacity_wheelchair = db.Column(INTEGER, name='capacity_wheelchair', nullable=False)
    low_floor           = db.Column(INTEGER, name='low_floor'          , nullable=False)
    lift_or_ramp        = db.Column(INTEGER, name='lift_or_ramp'       , nullable=False)
    
    vehicles = db.relationship('Vehicle',
                               primaryjoin='Vehicle.vehicle_type_id == VehicleType.id',
                               back_populates='vehicle_type',
                               uselist=True)
    
class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(INTEGER, name='id', primary_key=True)
    vehicle_type_id = db.Column(INTEGER, db.ForeignKey('vehicle_type.id'), name='vehicle_type_id', nullable=False)
    operator_id     = db.Column(INTEGER, db.ForeignKey('authority.id'   ), name='operator_id'    , nullable=False)
    from_datetime      = db.Column(TEXT   , name='from_datetime'     , nullable=True )
    to_datetime        = db.Column(TEXT   , name='to_datetime'       , nullable=True )
    operational_number = db.Column(INTEGER, name='operational_number', nullable=False)
    
    vehicle_type = db.relationship('VehicleType',
                                   primaryjoin='Vehicle.vehicle_type_id == VehicleType.id',
                                   back_populates='vehicles',
                                   uselist=False)
    operator     = db.relationship('Authority',
                                   primaryjoin='Vehicle.operator_id == Authority.id',
                                   back_populates='vehicles',
                                   uselist=False)

class ScheduledStopPoint(db.Model):
    __tablename__ = 'scheduled_stop_point'
    id = db.Column(INTEGER, name='id', primary_key=True)

    passenger_stop              = db.relationship('PassengerStop',
                                                  primaryjoin='ScheduledStopPoint.id == PassengerStop.scheduled_stop_point_id',
                                                  back_populates='scheduled_stop_point',
                                                  uselist=False)
    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='ScheduledStopPoint.id == JourneyPatternStopPoint.scheduled_stop_point_id',
                                                  back_populates='scheduled_stop_point',
                                                  uselist=True)
    service_links_from          = db.relationship('ServiceLink',
                                                  primaryjoin='ScheduledStopPoint.id == ServiceLink.point_from_id',
                                                  back_populates='point_from',
                                                  uselist=True)
    service_links_to            = db.relationship('ServiceLink',
                                                  primaryjoin='ScheduledStopPoint.id == ServiceLink.point_to_id',
                                                  back_populates='point_to',
                                                  uselist=True)

class DestinationDisplay(db.Model):
    __tablename__ = 'destination_display'
    id_db = db.Column(INTEGER, name='id_db', primary_key=True, autoincrement=True)
    id  = db.Column(INTEGER,                                          name='id' , nullable=True)
    via = db.Column(INTEGER, db.ForeignKey('destination_display.id'), name='via', nullable=True)
    front_text  = db.Column(TEXT, name='front_text' , nullable=False)
    public_code = db.Column(TEXT, name='public_code', nullable=False)

    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='DestinationDisplay.id == JourneyPatternStopPoint.destination_display_id',
                                                  back_populates='destination_display',
                                                  uselist=True)

class PassengerStop(db.Model):
    __tablename__ = 'passenger_stop'
    id = db.Column(INTEGER, name='id', primary_key=True)
    scheduled_stop_point_id = db.Column(INTEGER, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    quay_id                 = db.Column(INTEGER, db.ForeignKey('quay.id'                ), name='quay_id'                , nullable=False)

    scheduled_stop_point = db.relationship('ScheduledStopPoint',
                                           primaryjoin='PassengerStop.scheduled_stop_point_id == ScheduledStopPoint.id',
                                           back_populates='passenger_stop',
                                           uselist=False)
    quay                 = db.relationship('Quay',
                                           primaryjoin='PassengerStop.quay_id == Quay.id',
                                           back_populates='passenger_stops',
                                           uselist=False)

class Coordinate(db.Model):
    __tablename__ = 'coordinate'
    id = db.Column(INTEGER, name='id', primary_key=True, autoincrement=True)
    service_link_id_0 = db.Column(INTEGER, db.ForeignKey('service_link.id_0'), name='service_link_id_0', nullable=False)
    service_link_id_1 = db.Column(INTEGER, db.ForeignKey('service_link.id_1'), name='service_link_id_1', nullable=False)
    number    = db.Column(INTEGER, name='number'   , nullable=False)
    latitude  = db.Column(REAL   , name='latitude' , nullable=False)
    longitude = db.Column(REAL   , name='longitude', nullable=False)

    # Service link is a composite primary key, so we need to use SQLAlchemy's and_
    service_links = db.relationship('ServiceLink',
                                   primaryjoin='and_(Coordinate.service_link_id_0 == ServiceLink.id_0, Coordinate.service_link_id_1 == ServiceLink.id_1)',
                                   uselist=True)

class ServiceLink(db.Model):
    __tablename__ = 'service_link'
    id_0 = db.Column(INTEGER, name='id_0', primary_key=True)
    id_1 = db.Column(INTEGER, name='id_1', primary_key=True)
    point_from_id = db.Column(INTEGER, db.ForeignKey('scheduled_stop_point.id'),name='point_from_id', nullable=False)
    point_to_id   = db.Column(INTEGER, db.ForeignKey('scheduled_stop_point.id'),name='point_to_id'  , nullable=False)
    from_datetime  = db.Column(TEXT   , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TEXT   , name='to_datetime'   , nullable=True )
    distance       = db.Column(INTEGER, name='distance'      , nullable=False)
    transport_mode = db.Column(TEXT   , name='transport_mode', nullable=False)

    point_from = db.relationship('ScheduledStopPoint',
                                 primaryjoin='ServiceLink.point_from_id == ScheduledStopPoint.id',
                                 back_populates='service_links_from',
                                 uselist=False)
    point_to   = db.relationship('ScheduledStopPoint',
                                 primaryjoin='ServiceLink.point_to_id == ScheduledStopPoint.id',
                                 back_populates='service_links_to',
                                 uselist=False)

class DayType(db.Model):
    __tablename__ = 'day_type'
    id   = db.Column(TEXT, name='id', primary_key=True)
    days = db.Column(INTEGER, name='days', nullable=False) # Each day is stored in a bit, Monday is bit 0, Tuesday is bit 1, Wednesday is bit 2, etc.

class OperatingPeriod(db.Model):
    __tablename__ = 'operating_period'
    id = db.Column(INTEGER, name='id', primary_key=True)
    from_datetime = db.Column(TEXT, name='from_datetime', nullable=False)
    to_datetime   = db.Column(TEXT, name='to_datetime'  , nullable=False)

class Network(db.Model):
    __tablename__ = 'network'
    id = db.Column(INTEGER, name='id', primary_key=True)
    authority_id = db.Column(INTEGER, db.ForeignKey('authority.id'), name='authority_id', nullable=False)
    name = db.Column(TEXT, name='name', nullable=False)

    authority = db.relationship('Authority',
                                primaryjoin='Network.authority_id == Authority.id',
                                back_populates='network',
                                uselist=False)
    lines     = db.relationship('Line',
                                primaryjoin='Network.id == Line.network_id',
                                back_populates='network',
                                uselist=True )

class Line(db.Model):
    __tablename__ = 'line'
    id = db.Column(INTEGER, name='id', primary_key=True)
    network_id = db.Column(INTEGER, db.ForeignKey('network.id'), name='network_id', nullable=False)
    from_datetime  = db.Column(TEXT   , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TEXT   , name='to_datetime'   , nullable=True )
    name           = db.Column(TEXT   , name='name'          , nullable=False)
    public_code    = db.Column(TEXT   , name='public_code'   , nullable=False)
    private_code   = db.Column(INTEGER, name='private_code'  , nullable=False)
    transport_mode = db.Column(TEXT   , name='transport_mode', nullable=False)

    network = db.relationship('Network',
                              primaryjoin='Line.network_id == Network.id',
                              back_populates='lines',
                              uselist=False)


class Route(db.Model):
    __tablename__ = 'route'
    id = db.Column(INTEGER, name='id', primary_key=True)
    line_id = db.Column(INTEGER, db.ForeignKey('line.id'), name='line_id', nullable=False)
    name      = db.Column(TEXT, name='name'     , nullable=False)
    direction = db.Column(TEXT, name='direction', nullable=False)

    journey_patterns = db.relationship('JourneyPattern',
                                       primaryjoin='Route.id == JourneyPattern.route_id',
                                       back_populates='route',
                                       uselist=True)

class PointOnRoute(db.Model):
    __tablename__ = 'point_on_route'
    id = db.Column(INTEGER, name='id', primary_key=True)
    route_id                = db.Column(INTEGER, db.ForeignKey('route.id'               ), name='route_id'               , nullable=False)
    scheduled_stop_point_id = db.Column(INTEGER, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    order = db.Column(INTEGER, name='order', nullable=False)

    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='PointOnRoute.id == JourneyPatternStopPoint.point_on_route_id',
                                                  back_populates='point_on_route',
                                                  uselist=True)
    
class JourneyPattern(db.Model):
    __tablename__ = 'journey_pattern'
    id = db.Column(INTEGER, name='id', primary_key=True)
    route_id = db.Column(INTEGER, db.ForeignKey('route.id'), name='route_id', nullable=False)

    journeys                     = db.relationship('Journey',
                                                  primaryjoin='JourneyPattern.id == Journey.journey_pattern_id',
                                                  back_populates='journey_pattern',
                                                  uselist=True)
    route                       = db.relationship('Route',
                                                  primaryjoin='JourneyPattern.route_id == Route.id',
                                                  back_populates='journey_patterns',
                                                  uselist=False)
    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='JourneyPattern.id == JourneyPatternStopPoint.journey_pattern_id',
                                                  back_populates='journey_pattern',
                                                  uselist=True)

class JourneyPatternStopPoint(db.Model):
    __tablename__ = 'journey_pattern_stop_point'
    journey_pattern_id = db.Column(INTEGER, db.ForeignKey('journey_pattern.id'), name='journey_pattern_id', nullable=False, primary_key=True)
    point_on_route_id  = db.Column(INTEGER, db.ForeignKey('point_on_route.id' ), name='point_on_route_id' , nullable=False, primary_key=True)
    scheduled_stop_point_id = db.Column(INTEGER, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    destination_display_id  = db.Column(INTEGER, db.ForeignKey('destination_display.id' ), name='destination_display_id' , nullable=True )    
    alighting    = db.Column(INTEGER, name='alighting'   , nullable=False)
    boarding     = db.Column(INTEGER, name='boarding'    , nullable=False)
    request_stop = db.Column(INTEGER, name='request_stop', nullable=False)
    order        = db.Column(INTEGER, name='order'       , nullable=False)

    journey_pattern      = db.relationship('JourneyPattern',
                                           primaryjoin='JourneyPatternStopPoint.journey_pattern_id == JourneyPattern.id',
                                           back_populates='journey_pattern_stop_points',
                                           uselist=False)
    point_on_route       = db.relationship('PointOnRoute',
                                           primaryjoin='JourneyPatternStopPoint.point_on_route_id == PointOnRoute.id',
                                           back_populates='journey_pattern_stop_points',
                                           uselist=False)
    scheduled_stop_point = db.relationship('ScheduledStopPoint',
                                           primaryjoin='JourneyPatternStopPoint.scheduled_stop_point_id == ScheduledStopPoint.id',
                                           back_populates='journey_pattern_stop_points',
                                           uselist=False)
    destination_display  = db.relationship('DestinationDisplay',
                                           primaryjoin='JourneyPatternStopPoint.destination_display_id == DestinationDisplay.id',
                                           back_populates='journey_pattern_stop_points',
                                           uselist=False)
    
class JourneyPatternServiceLink(db.Model):
    __tablename__ = 'journey_pattern_service_link'
    id = db.Column(TEXT, name='id', nullable=False, primary_key=True)
    service_link_id_0 = db.Column(INTEGER, db.ForeignKey('service_link.id_0'), name='service_link_id_0', nullable=False)
    service_link_id_1 = db.Column(INTEGER, db.ForeignKey('service_link.id_1'), name='service_link_id_1', nullable=False)
    order = db.Column(INTEGER, name='order', nullable=False)

class Journey(db.Model):
    __tablename__ = 'journey'
    id = db.Column(INTEGER, name='id', primary_key=True)
    journey_pattern_id = db.Column(INTEGER, db.ForeignKey('journey_pattern.id'), name='journey_pattern_id', nullable=False)
    operator_id        = db.Column(INTEGER, db.ForeignKey('authority.id'      ), name='operator_id'       , nullable=False)
    day_type_id        = db.Column(TEXT   , db.ForeignKey('day_type.id'       ), name='day_type_id'       , nullable=False)
    transport_mode = db.Column(TEXT, name='transport_mode', nullable=False)

    journey_pattern = db.relationship('JourneyPattern',
                                      primaryjoin='Journey.journey_pattern_id == JourneyPattern.id',
                                      back_populates='journeys',
                                      uselist=False)
    operator        = db.relationship('Authority',
                                      primaryjoin='Journey.operator_id == Authority.id',
                                      back_populates='journeys',
                                      uselist=False)

class JourneyTime(db.Model):
    __tablename__ = 'journey_time'
    id = db.Column(INTEGER, name='id', primary_key=True)
    journey_id = db.Column(INTEGER, db.ForeignKey('journey.id'), name='journey_id', nullable=False)
    jpsp_journey_pattern_id = db.Column(INTEGER, db.ForeignKey('journey_pattern_stop_point.journey_pattern_id'), name='jpsp_journey_pattern_id', nullable=False)
    jpsp_point_on_route_id  = db.Column(INTEGER, db.ForeignKey('journey_pattern_stop_point.point_on_route_id' ), name='jpsp_point_on_route_id' , nullable=False)
    arrival_time   = db.Column(TEXT, name='arrival_time'  , nullable=True)
    departure_time = db.Column(TEXT, name='departure_time', nullable=True)

class StopGroup(db.Model):
    '''Representation oof a stop group in the database 
    (multiple stops may share a common place name)'''
    __tablename__ = 'stop_group'
    id = db.Column(INTEGER, name='id', primary_key=True)
    latitude      = db.Column(REAL   , name='latitude'     , nullable=True )
    longitude     = db.Column(REAL   , name='longitude'    , nullable=True )
    from_datetime = db.Column(TEXT   , name='from_datetime', nullable=True )
    to_datetime   = db.Column(TEXT   , name='to_datetime'  , nullable=True )
    name          = db.Column(TEXT   , name='name'         , nullable=False)
    description   = db.Column(TEXT   , name='description'  , nullable=True )
    private_code  = db.Column(INTEGER, name='private_code' , nullable=False)
    
    stops = db.relationship('Stop',
                            primaryjoin='StopGroup.id == Stop.stop_group_id',
                            back_populates='stop_group',
                            uselist=True)

class Stop(db.Model):
    '''Representation of a stop, these are the actual bus stops/cabins'''
    __tablename__ = 'stop'
    id = db.Column(INTEGER, name='id', primary_key=True)
    stop_group_id = db.Column(INTEGER, db.ForeignKey('stop_group.id'), name='stop_group_id', nullable=True )
    authority_id  = db.Column(INTEGER, db.ForeignKey('authority.id' ), name='authority_id' , nullable=False)
    latitude       = db.Column(REAL   , name='latitude'      , nullable=False)
    longitude      = db.Column(REAL   , name='longitude'     , nullable=False)
    from_datetime  = db.Column(TEXT   , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TEXT   , name='to_datetime'   , nullable=True )
    name           = db.Column(TEXT   , name='name'          , nullable=False)
    name_short     = db.Column(TEXT   , name='name_short'    , nullable=True )
    private_code   = db.Column(INTEGER, name='private_code'  , nullable=True )
    transport_mode = db.Column(TEXT   , name='transport_mode', nullable=False)
    type           = db.Column(TEXT   , name='type'          , nullable=False)
    
    authority         = db.relationship('Authority',
                                        primaryjoin='Stop.authority_id == Authority.id',
                                        back_populates='stops',
                                        uselist=False)
    stop_group        = db.relationship('StopGroup',
                                        primaryjoin='Stop.stop_group_id == StopGroup.id',
                                        back_populates='stops',
                                        uselist=False)
    alternative_names = db.relationship('AlternativeName',
                                        primaryjoin='Stop.id == AlternativeName.stop_id',
                                        back_populates='stop',
                                        uselist=True)
    quays             = db.relationship('Quay',
                                        primaryjoin='Stop.id == Quay.stop_id',
                                        back_populates='stop',
                                        uselist=True)
    
class AlternativeName(db.Model):
    __tablename__ = 'stop_alternative_name'
    id = db.Column(INTEGER, name='id', primary_key=True, autoincrement=True)
    stop_id = db.Column(INTEGER, db.ForeignKey('stop.id'), name='stop_id', nullable=False) 
    name         = db.Column(TEXT, name='name'        , nullable=False)
    abbreviation = db.Column(TEXT, name='abbreviation', nullable=False)
    
    stop = db.relationship('Stop',
                           primaryjoin='AlternativeName.stop_id == Stop.id',
                           back_populates='alternative_names',
                           uselist=False)

class Quay(db.Model):
    __tablename__ = 'quay'
    id = db.Column(INTEGER, name='id', primary_key=True)
    stop_id = db.Column(INTEGER, db.ForeignKey('stop.id'), name='stop_id', nullable=False)
    latitude      = db.Column(REAL   , name='latitude'     , nullable=False)
    longitude     = db.Column(REAL   , name='longitude'    , nullable=False)
    from_datetime = db.Column(TEXT   , name='from_datetime', nullable=True )
    to_datetime   = db.Column(TEXT   , name='to_datetime'  , nullable=True )
    private_code  = db.Column(INTEGER, name='private_code' , nullable=True )
    public_code   = db.Column(TEXT   , name='public_code'  , nullable=True )

    stop            = db.relationship('Stop',
                                      primaryjoin='Quay.stop_id == Stop.id',
                                      back_populates='quays',
                                      uselist=False)
    passenger_stops = db.relationship('PassengerStop',
                                      primaryjoin='Quay.id == PassengerStop.quay_id',
                                      back_populates='quay',
                                      uselist=True)