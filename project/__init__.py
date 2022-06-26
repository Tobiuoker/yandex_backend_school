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

    @app.route("/delete/<id>", methods = ['DELETE'])
    @handle_exception(logger)
    def deleteNode(id):
        return delete_unit_handler(id, db, app)

    @app.route("/imports", methods = ['POST'])
    @handle_exception(logger)
    def importRoute():
        return import_handler(request, db, app=app)

    @app.route("/sales", methods = ['GET'])
    @handle_exception(logger)
    def sales():
        return sales_handler(request.args.get('date'), db, app)

    @app.route('/node/<id>/statistic', methods=['GET'])
    @handle_exception(logger)
    def statistics(id):
        return get_statistics(id, request.args.get('dateStart'), request.args.get('dateEnd'), app)

    return app

