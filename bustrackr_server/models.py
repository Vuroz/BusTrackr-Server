from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, SMALLINT, TIMESTAMP, TIME, CHAR, VARCHAR, NUMERIC, BOOLEAN
from bustrackr_server import db

class Authority(db.Model):
    '''Representation of an authority in the database'''
    __tablename__ = 'authority'
    id = db.Column(BIGINT, name='id', primary_key=True)
    from_datetime  = db.Column(TIMESTAMP  , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TIMESTAMP  , name='to_datetime'   , nullable=True )
    name           = db.Column(VARCHAR(64), name='name'          , nullable=True ) # Not all authorities have a name (for some reason?)
    name_legal     = db.Column(VARCHAR(64), name='name_legal'    , nullable=True ) # Not all authorities have a legal name (for some reason?)
    private_code   = db.Column(INTEGER    , name='private_code'  , nullable=True )
    company_number = db.Column(VARCHAR(32), name='company_number', nullable=True )
    type           = db.Column(VARCHAR(32), name='type'          , nullable=False)
        
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
    id = db.Column(BIGINT, name='id', primary_key=True)
    type                = db.Column(VARCHAR(16), name='type'               , nullable=False)
    manufacturer        = db.Column(VARCHAR(32), name='manufacturer'       , nullable=True ) # Not all vehicles have a manufacturer (for some reason?)
    model_year          = db.Column(SMALLINT   , name='model_year'         , nullable=True ) # I think all vehicles have a model year, but leave it as nullable just in case
    fuel_type           = db.Column(VARCHAR(16), name='fuel_type'          , nullable=True ) # Not all vehicles have a fuel type (for some reason?)
    capacity_seated     = db.Column(SMALLINT   , name='capacity_seated'    , nullable=False)
    capacity_standing   = db.Column(SMALLINT   , name='capacity_standing'  , nullable=False)
    capacity_pushchair  = db.Column(SMALLINT   , name='capacity_pushchair' , nullable=False)
    capacity_wheelchair = db.Column(SMALLINT   , name='capacity_wheelchair', nullable=False)
    low_floor           = db.Column(SMALLINT   , name='low_floor'          , nullable=False)
    lift_or_ramp        = db.Column(SMALLINT   , name='lift_or_ramp'       , nullable=False)
    
    vehicles = db.relationship('Vehicle',
                               primaryjoin='Vehicle.vehicle_type_id == VehicleType.id',
                               back_populates='vehicle_type',
                               uselist=True)
    
class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(BIGINT, name='id', primary_key=True)
    vehicle_type_id = db.Column(BIGINT, db.ForeignKey('vehicle_type.id'), name='vehicle_type_id', nullable=False)
    operator_id     = db.Column(BIGINT, db.ForeignKey('authority.id'   ), name='operator_id'    , nullable=False)
    from_datetime      = db.Column(TIMESTAMP, name='from_datetime'     , nullable=True )
    to_datetime        = db.Column(TIMESTAMP, name='to_datetime'       , nullable=True )
    operational_number = db.Column(INTEGER  , name='operational_number', nullable=False)
    
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
    id = db.Column(BIGINT, name='id', primary_key=True)

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
    id  = db.Column(BIGINT,                                          name='id' , nullable=True, unique=True)
    via = db.Column(BIGINT, db.ForeignKey('destination_display.id'), name='via', nullable=True)
    front_text  = db.Column(VARCHAR(64), name='front_text' , nullable=True )
    public_code = db.Column(VARCHAR(16), name='public_code', nullable=True)

    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='DestinationDisplay.id == JourneyPatternStopPoint.destination_display_id',
                                                  back_populates='destination_display',
                                                  uselist=True)

class PassengerStop(db.Model):
    __tablename__ = 'passenger_stop'
    id = db.Column(BIGINT, name='id', primary_key=True)
    scheduled_stop_point_id = db.Column(BIGINT, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    quay_id                 = db.Column(BIGINT, db.ForeignKey('quay.id'                ), name='quay_id'                , nullable=False)

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
    id = db.Column(BIGINT, name='id', primary_key=True, autoincrement=True)
    service_link_id_0 = db.Column(BIGINT, name='service_link_id_0', nullable=False)
    service_link_id_1 = db.Column(BIGINT, name='service_link_id_1', nullable=False)
    number    = db.Column(SMALLINT    , name='number'   , nullable=False)
    latitude  = db.Column(NUMERIC(8,6), name='latitude' , nullable=False) # 8 digits, 6 decimal places, we only work with swedish coordinates
    longitude = db.Column(NUMERIC(8,6), name='longitude', nullable=False) # 8 digits, 6 decimal places, we only work with swedish coordinates

    # Composite foreign key referencing both columns (id_0, id_1) in service_link
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['service_link_id_0', 'service_link_id_1'],
            ['service_link.id_0', 'service_link.id_1']
        ),
    )

    # Service link is a composite primary key, so we need to use SQLAlchemy's and_
    service_links = db.relationship('ServiceLink',
                                   primaryjoin='and_(Coordinate.service_link_id_0 == ServiceLink.id_0, Coordinate.service_link_id_1 == ServiceLink.id_1)',
                                   uselist=True)

class ServiceLink(db.Model):
    __tablename__ = 'service_link'
    id_0 = db.Column(BIGINT, name='id_0', primary_key=True)
    id_1 = db.Column(BIGINT, name='id_1', primary_key=True)
    point_from_id = db.Column(BIGINT, db.ForeignKey('scheduled_stop_point.id'),name='point_from_id', nullable=False)
    point_to_id   = db.Column(BIGINT, db.ForeignKey('scheduled_stop_point.id'),name='point_to_id'  , nullable=False)
    from_datetime  = db.Column(TIMESTAMP  , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TIMESTAMP  , name='to_datetime'   , nullable=True )
    distance       = db.Column(INTEGER    , name='distance'      , nullable=False)
    transport_mode = db.Column(VARCHAR(16), name='transport_mode', nullable=False)

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
    id   = db.Column(CHAR(32), name='id', primary_key=True)
    days = db.Column(SMALLINT, name='days', nullable=False) # Each day is stored in a bit, Monday is bit 0, Tuesday is bit 1, Wednesday is bit 2, etc.

class OperatingPeriod(db.Model):
    __tablename__ = 'operating_period'
    id = db.Column(BIGINT, name='id', primary_key=True)
    from_datetime = db.Column(TIMESTAMP, name='from_datetime', nullable=False)
    to_datetime   = db.Column(TIMESTAMP, name='to_datetime'  , nullable=False)

class Network(db.Model):
    __tablename__ = 'network'
    id = db.Column(BIGINT, name='id', primary_key=True)
    authority_id = db.Column(BIGINT, db.ForeignKey('authority.id'), name='authority_id', nullable=False)
    name = db.Column(VARCHAR(64), name='name', nullable=False)

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
    id = db.Column(BIGINT, name='id', primary_key=True)
    network_id = db.Column(BIGINT, db.ForeignKey('network.id'), name='network_id', nullable=False)
    from_datetime  = db.Column(TIMESTAMP  , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TIMESTAMP  , name='to_datetime'   , nullable=True )
    name           = db.Column(VARCHAR(64), name='name'          , nullable=False)
    public_code    = db.Column(VARCHAR(16), name='public_code'   , nullable=True )
    private_code   = db.Column(INTEGER    , name='private_code'  , nullable=False)
    transport_mode = db.Column(VARCHAR(16), name='transport_mode', nullable=False)

    network = db.relationship('Network',
                              primaryjoin='Line.network_id == Network.id',
                              back_populates='lines',
                              uselist=False)


class Route(db.Model):
    __tablename__ = 'route'
    id = db.Column(BIGINT, name='id', primary_key=True)
    line_id = db.Column(BIGINT, db.ForeignKey('line.id'), name='line_id', nullable=False)
    name      = db.Column(VARCHAR(64), name='name'     , nullable=False)
    direction = db.Column(VARCHAR(8), name='direction', nullable=False) # Will only ever be 'inbound' or 'outbound' (perhaps convert to boolean?)

    journey_patterns = db.relationship('JourneyPattern',
                                       primaryjoin='Route.id == JourneyPattern.route_id',
                                       back_populates='route',
                                       uselist=True)

class PointOnRoute(db.Model):
    __tablename__ = 'point_on_route'
    id = db.Column(BIGINT, name='id', primary_key=True)
    route_id                = db.Column(BIGINT, db.ForeignKey('route.id'               ), name='route_id'               , nullable=False)
    scheduled_stop_point_id = db.Column(BIGINT, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    order = db.Column(SMALLINT, name='order', nullable=False)

    journey_pattern_stop_points = db.relationship('JourneyPatternStopPoint',
                                                  primaryjoin='PointOnRoute.id == JourneyPatternStopPoint.point_on_route_id',
                                                  back_populates='point_on_route',
                                                  uselist=True)
    
class JourneyPattern(db.Model):
    __tablename__ = 'journey_pattern'
    id = db.Column(BIGINT, name='id', primary_key=True)
    route_id = db.Column(BIGINT, db.ForeignKey('route.id'), name='route_id', nullable=False)

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
    journey_pattern_id = db.Column(BIGINT, db.ForeignKey('journey_pattern.id'), name='journey_pattern_id', nullable=False, primary_key=True)
    point_on_route_id  = db.Column(BIGINT, db.ForeignKey('point_on_route.id' ), name='point_on_route_id' , nullable=False, primary_key=True)
    scheduled_stop_point_id = db.Column(BIGINT, db.ForeignKey('scheduled_stop_point.id'), name='scheduled_stop_point_id', nullable=False)
    destination_display_id  = db.Column(BIGINT, db.ForeignKey('destination_display.id' ), name='destination_display_id' , nullable=True )    
    alighting    = db.Column(BOOLEAN , name='alighting'   , nullable=False)
    boarding     = db.Column(BOOLEAN , name='boarding'    , nullable=False)
    request_stop = db.Column(BOOLEAN , name='request_stop', nullable=False)
    order        = db.Column(SMALLINT, name='order'       , nullable=False)

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
    id = db.Column(VARCHAR(16), name='id', nullable=False, primary_key=True)
    service_link_id_0 = db.Column(BIGINT, name='service_link_id_0', nullable=False)
    service_link_id_1 = db.Column(BIGINT, name='service_link_id_1', nullable=False)
    order = db.Column(SMALLINT, name='order', nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['service_link_id_0', 'service_link_id_1'],
            ['service_link.id_0', 'service_link.id_1']
        ),
    )

class Journey(db.Model):
    __tablename__ = 'journey'
    id = db.Column(BIGINT, name='id', primary_key=True)
    journey_pattern_id = db.Column(BIGINT  , db.ForeignKey('journey_pattern.id'), name='journey_pattern_id', nullable=False)
    operator_id        = db.Column(BIGINT  , db.ForeignKey('authority.id'      ), name='operator_id'       , nullable=False)
    day_type_id        = db.Column(CHAR(32), db.ForeignKey('day_type.id'       ), name='day_type_id'       , nullable=False)
    transport_mode = db.Column(VARCHAR(16), name='transport_mode', nullable=False)

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
    id = db.Column(BIGINT, name='id', primary_key=True)
    journey_id = db.Column(BIGINT, db.ForeignKey('journey.id'), name='journey_id', nullable=False)
    jpsp_journey_pattern_id = db.Column(BIGINT, name='jpsp_journey_pattern_id', nullable=False)
    jpsp_point_on_route_id  = db.Column(BIGINT, name='jpsp_point_on_route_id' , nullable=False)
    arrival_time   = db.Column(TIME, name='arrival_time'  , nullable=True)
    departure_time = db.Column(TIME, name='departure_time', nullable=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['jpsp_journey_pattern_id',                       'jpsp_point_on_route_id'],
            ['journey_pattern_stop_point.journey_pattern_id', 'journey_pattern_stop_point.point_on_route_id']
        ),
    )

class StopGroup(db.Model):
    '''Representation oof a stop group in the database 
    (multiple stops may share a common place name)'''
    __tablename__ = 'stop_group'
    id = db.Column(BIGINT, name='id', primary_key=True)
    latitude      = db.Column(NUMERIC(8,6), name='latitude'     , nullable=True ) # 8 digits, 6 decimal places, we only work with swedish coordinates
    longitude     = db.Column(NUMERIC(8,6), name='longitude'    , nullable=True ) # 8 digits, 6 decimal places, we only work with swedish coordinates
    from_datetime = db.Column(TIMESTAMP   , name='from_datetime', nullable=True )
    to_datetime   = db.Column(TIMESTAMP   , name='to_datetime'  , nullable=True )
    name          = db.Column(VARCHAR(48) , name='name'         , nullable=False)
    description   = db.Column(VARCHAR(32) , name='description'  , nullable=True )
    private_code  = db.Column(INTEGER     , name='private_code' , nullable=False)
    
    stops = db.relationship('Stop',
                            primaryjoin='StopGroup.id == Stop.stop_group_id',
                            back_populates='stop_group',
                            uselist=True)

class Stop(db.Model):
    '''Representation of a stop, these are the actual bus stops/cabins'''
    __tablename__ = 'stop'
    id = db.Column(BIGINT, name='id', primary_key=True)
    stop_group_id = db.Column(BIGINT, db.ForeignKey('stop_group.id'), name='stop_group_id', nullable=True )
    authority_id  = db.Column(BIGINT, db.ForeignKey('authority.id' ), name='authority_id' , nullable=False)
    latitude       = db.Column(NUMERIC(15,13), name='latitude'      , nullable=False)
    longitude      = db.Column(NUMERIC(15,13), name='longitude'     , nullable=False)
    from_datetime  = db.Column(TIMESTAMP     , name='from_datetime' , nullable=True )
    to_datetime    = db.Column(TIMESTAMP     , name='to_datetime'   , nullable=True )
    name           = db.Column(VARCHAR(64)   , name='name'          , nullable=False)
    name_short     = db.Column(VARCHAR(16)   , name='name_short'    , nullable=True )
    private_code   = db.Column(INTEGER       , name='private_code'  , nullable=True )
    transport_mode = db.Column(VARCHAR(16)   , name='transport_mode', nullable=False)
    type           = db.Column(VARCHAR(16)   , name='type'          , nullable=False)
    
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
    stop_id = db.Column(BIGINT, db.ForeignKey('stop.id'), name='stop_id', nullable=False) 
    name         = db.Column(TEXT, name='name'        , nullable=False)
    abbreviation = db.Column(TEXT, name='abbreviation', nullable=False)
    
    stop = db.relationship('Stop',
                           primaryjoin='AlternativeName.stop_id == Stop.id',
                           back_populates='alternative_names',
                           uselist=False)

class Quay(db.Model):
    __tablename__ = 'quay'
    id = db.Column(BIGINT, name='id', primary_key=True)
    stop_id = db.Column(BIGINT, db.ForeignKey('stop.id'), name='stop_id', nullable=False)
    latitude      = db.Column(NUMERIC(15,13), name='latitude'     , nullable=False)
    longitude     = db.Column(NUMERIC(15,13), name='longitude'    , nullable=False)
    from_datetime = db.Column(TIMESTAMP     , name='from_datetime', nullable=True )
    to_datetime   = db.Column(TIMESTAMP     , name='to_datetime'  , nullable=True )
    private_code  = db.Column(INTEGER       , name='private_code' , nullable=True )
    public_code   = db.Column(VARCHAR(8)    , name='public_code'  , nullable=True )

    stop            = db.relationship('Stop',
                                      primaryjoin='Quay.stop_id == Stop.id',
                                      back_populates='quays',
                                      uselist=False)
    passenger_stops = db.relationship('PassengerStop',
                                      primaryjoin='Quay.id == PassengerStop.quay_id',
                                      back_populates='quay',
                                      uselist=True)