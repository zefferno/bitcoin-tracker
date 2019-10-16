import os


class Config():
    APP_NAME = "Bitcoin Price Tracker"
    TCP_PORT = 80
    DEBUG = False
    BC_TRACKER_URL = "https://api.coinmarketcap.com/v1/ticker/bitcoin/"
    DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), "db.sqlite")
    DB_SCHEMA = os.path.join(os.path.abspath(os.path.dirname(__file__)), "schema.sql")
    DB_BC_AVERAGE_TIME = 10
    DB_BC_COLLECTION_TIME = 1
    DB_BC_CLEANUP_KEEP_ITEMS = 1
    PAGE_REFRESH = 5
