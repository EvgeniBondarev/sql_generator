import configparser

config = configparser.ConfigParser()

config.read('config.ini')

DB_HOST = config.get('database', 'DB_HOST')
DB_USER = config.get('database', 'DB_USER')
DB_PASSWORD = config.get('database', 'DB_PASSWORD')
DB_NAME = config.get('database', 'DB_NAME')
