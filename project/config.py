import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@db/postgresDB"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/postgres"
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False