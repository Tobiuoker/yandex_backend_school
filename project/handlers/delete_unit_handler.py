
from typing import List
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from project.db.schema import ShopUnit

def delete_unit_handler(id_to_delete: str, db: SQLAlchemy):
    """
        Удаление объекта и всех его дочерних элементов
    """
    unit = ShopUnit.get_data_by_id(id_to_delete)
    if not unit:
        return make_response("Категория/товар не найден.", 404)

    units_to_delete = [id_to_delete]

    units_to_delete += get_children_ids(unit.as_dict())

    delete_units(units_to_delete, db)

    return make_response("Удаление прошло успешно.", 200) 


def get_children_ids(node: dict):
    """
        Рекурсивно достаю children каждого элемента
    """
    children = node["children"] if node.get("children") else []

    children_objects = list(map(lambda x: ShopUnit.get_data_by_id(x).as_dict(), children))

    for child_unit in children_objects:
        children += get_children_ids(child_unit)
    
    return children if children else []

def delete_units(units_to_delete: List[str], db: SQLAlchemy):
    """
        Bulk delete всех собранных айдишек
    """
    db.session.query(ShopUnit).filter(ShopUnit.id.in_(units_to_delete)).delete()
    db.session.commit()
