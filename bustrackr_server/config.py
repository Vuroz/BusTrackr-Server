import os
from dotenv import dotenv_values

curr_path = os.path.dirname(__file__)
dev_env_path = os.path.join(curr_path, '../.env')

env_path = os.getenv('FLASK_ENV_PATH', dev_env_path)

env_file = dotenv_values(dotenv_path=env_path)

database_user = env_file['DATABASE_USER']
database_pass = env_file['DATABASE_PASS']   
database_host = env_file['DATABASE_HOST']
database_port = env_file['DATABASE_PORT']
database_database = env_file['DATABASE_DATABASE']

class Config:
    SECRET_KEY = env_file['FLASK_SECRET']
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://{database_user}:{database_pass}@{database_host}:{database_port}/{database_database}'