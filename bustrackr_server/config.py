import os
from dotenv import dotenv_values

curr_path = os.path.dirname(__file__)
dev_env_path = os.path.join(curr_path, '../.env')
dev_env_file = dotenv_values(dotenv_path=dev_env_path)

env_mode = os.getenv('FLASK_ENV', 'development')

def get_env_value(key):
    if env_mode == 'development':
        return dev_env_file[key]
    else:
        return os.getenv(key)

database_user = get_env_value('DATABASE_USER')
database_pass = get_env_value('DATABASE_PASS')   
database_host = get_env_value('DATABASE_HOST')
database_port = get_env_value('DATABASE_PORT')
database_database = get_env_value('DATABASE_DATABASE')

trafiklab_url = get_env_value('TRAFIKLAB_URL')
trafiklab_key = get_env_value('TRAFIKLAB_KEY')

class Config:
    SECRET_KEY = get_env_value('FLASK_SECRET')
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://{database_user}:{database_pass}@{database_host}:{database_port}/{database_database}'
    REDIS_HOST = get_env_value('REDIS_HOST')
    REDIS_PORT = get_env_value('REDIS_PORT')
    REDIS_PASS = get_env_value('REDIS_PASS')
    REDIS_DB = int(get_env_value('REDIS_DB'))
    API_URL = f'{trafiklab_url}?key={trafiklab_key}'
    JWT_SECRET = get_env_value('JWT_SECRET')
    ENV = os.getenv('FLASK_ENV', 'development')