from datetime import datetime
from typing import List
from dateutil.parser import parse
from project.db.schema import ShopUnit, ShopUnitType

def parse_str_to_date(strdate):
    """
        Парсит строку с датой вида 2022-02-02T12:00:00.000Z в формат datetime
    """
    return datetime.strptime(str(parse(strdate))[:-6], "%Y-%m-%d %H:%M:%S")

def shop_unit_list_to_dict_list_without_children(data: List[ShopUnit]) -> List[dict]:
    """
        Превращает массив объектов ShopUnit в массив словарей, удаляя параметр children
    """
    result = []
    for i in data:
        data_dict = i.as_dict()
        del data_dict["children"]
        result += [data_dict]
    return result

def get_average_price(node: dict) -> dict:
    """
        Рекурсивно считает среднюю цену для товара и его детей (типа CATEGORY)
    """
    children = node["children"] if node.get("children") else []

    children_objects = list(map(lambda x: ShopUnit.get_data_by_id(x).as_dict(), children))

    avgPrice = []
    for i in children_objects:
        i = get_average_price(i)
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
    return node

def get_children(node: dict) -> dict:
    """
        Рекурсивно получаем информацию о дочерних элементах
    """
    children = node["children"] if node.get("children") else []

    children_objects = list(map(lambda x: ShopUnit.get_data_by_id(x).as_dict(), children))

    for i in range(len(children_objects)):
        children_objects[i] = get_children(children_objects[i])
    
    if children_objects:
        node["children"] = children_objects
    return node