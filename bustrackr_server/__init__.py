from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from bustrackr_server.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from bustrackr_server import models # Need to import
# from bustrackr_server.data_parser import process_static_data # This file is not included in the repo yet
import os

def fix_database():
    with app.app_context():
        db.create_all() # Create all the tables
        # process_static_data()

from bustrackr_server import routes