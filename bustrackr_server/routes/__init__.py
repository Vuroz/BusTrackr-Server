from flask import Flask, Blueprint
from bustrackr_server.routes.quays import quays_bp
from bustrackr_server.routes.stops import stops_bp

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(quays_bp)
api_bp.register_blueprint(stops_bp)

def register_routes(app: Flask):
    app.register_blueprint(api_bp, url_prefix='/api')