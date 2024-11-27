from os import path
from dotenv import dotenv_values

curr_path = path.dirname(__file__)
env_path = path.join(curr_path, '../.env')

env_file = dotenv_values(dotenv_path=env_path)
database_file = env_file['DATABASE_FILE']

class Config:
    SECRET_KEY = env_file['FLASK_SECRET']
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_file}'