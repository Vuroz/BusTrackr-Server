from flask import Flask, Blueprint, session
from bustrackr_server.routes.quays import quays_bp
from bustrackr_server.routes.stops import stops_bp
from bustrackr_server.routes.stop_groups import groups_bp
from bustrackr_server.routes.live import live_bp
from bustrackr_server.routes.journey_details import journey_details_bp
from bustrackr_server.routes.account import account_bp

from threading import Timer
import time

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(quays_bp)
api_bp.register_blueprint(stops_bp)
api_bp.register_blueprint(groups_bp)
api_bp.register_blueprint(live_bp)
api_bp.register_blueprint(journey_details_bp)
api_bp.register_blueprint(account_bp)

# TODO: Find a better place for the session stuff
session_timers = {} # Stores all the timers
session_states = {} # We cannot access the session outside the request context, so this is needed, simply stores TRUE if active

def set_session_inactive(session_id):
    if session_id in session_states:
        del session_states[session_id] # The len of this is checked to see if anyone is active

@api_bp.before_request
def extend_timer():
    global session_timers, session_states

    # Check if the session has a id, else create and set as active
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(time.time())
        session['session_id'] = session_id

    # We want to extend the timer, cancel the last one
    if session_id in session_timers:
        session_timers[session_id].cancel()

    session_states[session_id] = True

    # Create a new timer and start it
    timer = Timer(15, set_session_inactive, args=(session_id,))
    session_timers[session_id] = timer
    timer.start()

def register_routes(app: Flask):
    app.register_blueprint(api_bp, url_prefix='/api')