class Config(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Brian8053@@127.0.0.1:5432/orderManagementSystem'
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345678@172.17.0.1:5432/orderManagementSystem'
    SECRET_KEY = 'some-secret-key'

class ProductionConfig(Config):
    DEBUG = False