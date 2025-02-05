import configparser

config = configparser.ConfigParser()

config.read('config.ini')

DB_HOST = config.get('database', 'DB_HOST')
DB_USER = config.get('database', 'DB_USER')
DB_PASSWORD = config.get('database', 'DB_PASSWORD')
DB_NAME = config.get('database', 'DB_NAME')
TABLE_CATEGORIES = config.get('database', 'TABLE_CATEGORIES')
TABLE_PRODUCTS = config.get('database', 'TABLE_PRODUCTS')
TABLE_ATTRIBUTES = config.get('database', 'TABLE_ATTRIBUTES')


