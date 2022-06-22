from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from project.db.schema import ShopUnitType, ShopUnit

def get_unit_handler(id: str, db: SQLAlchemy, app: Flask):
    """
        Выдает информацию об элементе, по его айди. Также есть информация о его дочерних элементах
    """
    unit_to_get = ShopUnit.get_data_by_id(id)

    if not unit_to_get:
        return make_response("Категория/товар не найден.", 404)

    unit_to_get_with_children = getChildrenDict(unit_to_get.as_dict(), app)

    return make_response(jsonify(unit_to_get_with_children), 200)

    
def getChildrenDict(node, app: Flask):
    """
        Рекурсивно получаем информацию о дочрних элементах, попутно считая среднюю цену
    """
    children = node["children"] if node.get("children") else []

    children_objects = list(map(lambda x: ShopUnit.get_data_by_id(x).as_dict(), children))

    avgPrice = []
    for i in children_objects:
        i = getChildrenDict(i, app)
        if i.get("type") == ShopUnitType.category.value:
            if i.get("price"):
                categoryAvgPrice = i.get("price")
                quantity = len(i.get("children"))

                totalPrice = categoryAvgPrice * quantity

                avgPrice += [totalPrice // quantity + (1 if x < totalPrice % quantity else 0) for x in range (quantity)]
        else:
            if i.get("price"):
                avgPrice += [i.get("price")]
    
    if node.get("type") == ShopUnitType.category.value:
        node["price"] = int(sum(avgPrice)/len(avgPrice)) if avgPrice else None
    
    if children_objects:
        node["children"] = children_objects
    return node