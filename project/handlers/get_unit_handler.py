from flask import jsonify, abort, make_response
from project.db.schema import ShopUnit

from project.handlers.util import get_children

def get_unit_handler(id: str):
    """
        Выдает информацию об элементе, по его айди. Также есть информация о его дочерних элементах
    """
    unit_to_get = ShopUnit.get_data_by_id(id)

    if not unit_to_get:
        abort(404)

    unit_to_get_with_children = get_children(unit_to_get.as_dict())

    return make_response(jsonify(unit_to_get_with_children), 200)