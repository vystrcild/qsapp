from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SECRET_KEY = environ.get('SECRET_KEY')


class DevConfig(Config):
    # Flask Configuration
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    DATABASE_URI = environ.get('DEV_DATABASE_URI')
    environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Flask-Cache
    CACHE_TYPE = "filesystem"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_DIR = "cache"

    # DB connection
    MYSQL_URL = environ.get('MYSQL_URL')
    MYSQL_LOGIN = environ.get('MYSQL_LOGIN')
    MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD')

    # Withing API
    CLIENT_ID_WITHINGS = environ.get('CLIENT_ID_WITHINGS')
    CLIENT_SECRET_WITHINGS = environ.get('CLIENT_SECRET_WITHINGS')
    AUTH_URL_WITHINGS = environ.get('AUTH_URL_WITHINGS')
    TOKEN_URL_WITHINGS = environ.get('TOKEN_URL_WITHINGS')
    CALLBACK_WITHINGS = environ.get('CALLBACK_WITHINGS')
    WBS_API_URL = environ.get('WBS_API_URL')
    TOKEN_WITHING = environ.get('TOKEN_WITHINGS')

    # MyFitnessPal API
    MYFITNESSPAL_USER = environ.get('MYFITNESSPAL_USER')
    MYFITNESSPAL_PASS = environ.get('MYFITNESSPAL_PASS')

    # OURA ring API
    CLIENT_ID_OURA = environ.get('CLIENT_ID_OURA')
    CLIENT_SECRET_OURA = environ.get('CLIENT_SECRET_OURA')
    AUTH_URL_OURA = environ.get('AUTH_URL_OURA')
    TOKEN_URL_OURA = environ.get('TOKEN_URL_OURA')
    TOKEN_OURA = environ.get('TOKEN_OURA')
