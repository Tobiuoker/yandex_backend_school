import logging
from flask import Flask, request
from project.db import db

from flask_swagger_ui import get_swaggerui_blueprint

from project.exception_handler import handle_exception

from project.handlers.import_handler import import_handler
from project.handlers.sales_handler import sales_handler
from project.handlers.delete_unit_handler import delete_unit_handler
from project.handlers.get_unit_handler import get_unit_handler
from project.handlers.statistics_handler import get_statistics

logger = logging.getLogger(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)

temp = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Товары",
                "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "parentId": None,
                "children": []
            }
        ],
        "updateDate": "2029-02-01T12:00:00Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999,
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2029-02-02T12:00:00Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": "Samson 70\" LED UHD Smart",
                "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 32999
            },
            {
                "type": "OFFER",
                "name": "Phyllis 50\" LED UHD Smarter",
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 49999
            }
        ],
        "updateDate": "2029-02-03T12:00:00Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Goldstar 65\" LED UHD LOL Very Smart",
                "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 69999
            }
        ],
        "updateDate": "2029-02-03T15:00:00Z"
    }
]

def create_app(config):
    app = Flask(__name__)

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    app.config.from_object(config)

    db.init_app(app)

    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    @app.route("/nodes/<id>")
    @handle_exception(logger)
    def getNode(id):
        return get_unit_handler(id)

    # @app.route("/delete/<id>")
    @app.route("/delete/<id>", methods = ['DELETE'])
    @handle_exception(logger)
    def deleteNode(id):
        return delete_unit_handler(id, db, app)

    @app.route("/imports", methods = ['POST'])
    @handle_exception(logger)
    def importRoute():
        return import_handler(request, db, app=app)

    # @app.route("/imports", methods=['GET'])
    # @handle_exception(logger)
    # def importRoute():
    #     return import_handler(temp, db, app=app)

    @app.route("/sales", methods = ['GET'])
    @handle_exception(logger)
    def sales():
        return sales_handler(request.args.get('date'), db, app)

    @app.route('/node/<id>/statistic', methods=['GET'])
    @handle_exception(logger)
    def statistics(id):
        return get_statistics(id, request.args.get('dateStart'), request.args.get('dateEnd'), app)

    return app

