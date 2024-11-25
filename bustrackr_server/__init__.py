from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from bustrackr_server.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from bustrackr_server import routes