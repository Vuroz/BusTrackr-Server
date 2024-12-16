from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from bustrackr_server.config import Config
from redis_om import redis, Migrator

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASS,
    db=Config.REDIS_DB,
    decode_responses=True,
    retry_on_error=[redis.exceptions.ConnectionError],
    retry_on_timeout=True
)

redis_client.flushall()
redis_client.flushdb()

from bustrackr_server.models_redis import VehicleLive

Migrator().run()

from bustrackr_server import models # Need to import
# from bustrackr_server.data_parser import process_static_data # This file is not included in the repo yet

def fix_redis():
    redis_client.flushall()
    redis_client.flushdb()
    Migrator().run()

def fix_database():
    with app.app_context():
        db.create_all() # Create all the tables
        db.session.commit()
        # process_static_data()

from bustrackr_server.routes import register_routes
register_routes(app)

from bustrackr_server.data_fetcher import do_fetch
do_fetch()