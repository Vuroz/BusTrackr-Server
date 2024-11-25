from os import path
from dotenv import dotenv_values

curr_path = path.dirname(__file__)
env_path = path.join(curr_path, '../.env')

env_file = dotenv_values(dotenv_path=env_path)

class Config:
    SECRET_KEY = env_file['FLASK_SECRET']