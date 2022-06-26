import collections
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from werkzeug import Request
from project.db.schema import ShopUnit, ShopUnitChanges, ShopUnitType
from flask import Flask, make_response

import json
import time

from project.handlers.util import parse_str_to_date, get_average_price

def import_handler(request: Request, db: SQLAlchemy, app: Flask):
    """
        Импортирует новые товары и/или категории. Товары/категории импортированные повторно обновляют текущие.

          - uuid товара или категории является уникальным среди товаров и категорий
          - родителем товара или категории может быть только категория
          - принадлежность к категории определяется полем parentId
          - товар или категория могут не иметь родителя
          - название элемента не может быть null
          - у категорий поле price должно содержать null
          - при обновлении товара/категории обновленными считаются **все** их параметры
          - при обновлении параметров элемента обязательно обновляется поле **date** в соответствии с временем обновления
          - в одном запросе не может быть двух элементов с одинаковым id
          - изменение типа элемента с товара на категорию или с категории на товар не допускается
          - при изменении товара, категории offer, сразу обновляется средняя цена его parent'а
          - при импорте сразу считается средняя цена для категорий 
    """
    new_data_to_upload = []
    parents_date_to_update = []

    # for dictionary in request:
    #     if not dictionary:
    #         return make_response("Невалидная схема документа или входные данные не верны.", 400)
    #     parsed_date = f'{parse_str_to_date(dictionary.get("updateDate"))}' 

    #     for item in dictionary.get("items"):
    #         parent = ShopUnit.get_data_by_id(item.get("parentId"))
    #         old_data_record = ShopUnit.get_data_by_id(item.get("id"))

    #         validate_importing_unit(item, parent)

    #         if not update_record_if_needed(item, old_data_record, parsed_date, db):
    #             db.session.add(parse_dict_to_shop_unit(item, parsed_date, app))

    #             if parent:
    #                 if parent.children:
    #                     parent.children = list(set([item.get("id")] + parent.children))
    #                 else:
    #                     parent.children = [item.get("id")]
                
    #             db.session.commit()
            
    #         if item.get("type") == ShopUnitType.offer.value and (parent and parent.type == ShopUnitType.category.value): 
    #             if (old_data_record and old_data_record.price != item.get("price")) or not old_data_record:
    #                 update_parent_average_price_if_needed(parent, db, parsed_date)
            
    #         if item.get("parentId"):
    #             parents_date_to_update += [(item.get("parentId"), parsed_date)]

    

    if request.headers['content-type'] != 'application/json':
        raise ValueError("Невалидная схема документа или входные данные не верны.")

    data = request.get_json()

    if check_for_duplicate_ids(data):
        raise ValueError("В одном запросе не может быть двух элементов с одинаковым id")

    parsed_date = f'{parse_str_to_date(data.get("updateDate"))}' 

    for item in data.get("items"):
        parent = ShopUnit.get_data_by_id(item.get("parentId"))
        old_data_record = ShopUnit.get_data_by_id(item.get("id"))

        validate_importing_unit(item, parent)

        if not update_record_if_needed(item, old_data_record, parsed_date, db):
            db.session.add(parse_dict_to_shop_unit(item, parsed_date, app))

            if parent:
                if parent.children:
                    parent.children = list(set([item.get("id")] + parent.children))
                else:
                    parent.children = [item.get("id")]
            
            db.session.commit()
        
        if item.get("type") == ShopUnitType.offer.value and (parent and parent.type == ShopUnitType.category.value): 
            if (old_data_record and old_data_record.price != item.get("price")) or not old_data_record:
                update_parent_average_price_if_needed(parent, db, parsed_date)
        
        if item.get("parentId"):
            parents_date_to_update += [(item.get("parentId"), parsed_date)]


    for (parentId, parsed_date) in parents_date_to_update:
        update_parent_date_if_needed(parentId, parsed_date)

    db.session.commit()
    return make_response("Вставка или обновление прошли успешно.", 200)

def update_parent_average_price_if_needed(parent: ShopUnit, db: SQLAlchemy, date: DateTime):
    """
        Рекурсивно обновляю среднюю цену категории
    """
    parent_of_parent = ShopUnit.get_data_by_id(parent.parentId)
    
    new_average_price = get_average_price(parent.as_dict()).get("price")

    if new_average_price != parent.price:
        log_price_changes(parent, new_average_price, date)
        parent.price = new_average_price

    db.session.commit()

    if parent_of_parent:
        update_parent_average_price_if_needed(parent_of_parent, db, date)

def parse_dict_to_shop_unit(data: dict, parsed_date: DateTime, app: Flask) -> ShopUnit:
    """
        Парсит словарь в модельку

        data: словарь с невалидированными данными
        parsed_date: форматированная дата вида "2022-02-02 12:00:00"

        return: спарсенную модельку типа ShopUnit
    """
    shop_unit = ShopUnit()
    shop_unit.id = data.get("id")
    shop_unit.name = data.get("name")
    shop_unit.date = parsed_date
    shop_unit.parentId = data.get("parentId")
    shop_unit.type = data.get("type")
    shop_unit.children = data.get("children")

    if data.get("type") != ShopUnitType.category.value:
        log_price_changes(shop_unit, data.get("price"), parsed_date)

    shop_unit.price = data.get("price")

    return shop_unit

def update_record_if_needed(new_record: dict, old_record: ShopUnit, parsed_date: DateTime, db: SQLAlchemy) -> bool:
    """
        Обновляет данные, если они уже имеются в базе

        new_record: новое значение для строки с таким же айди
        db: объект базы данных

        return: bool значение (было ли произведено обновление)
    """
    if old_record:
        if old_record.type != new_record.get("type"):
            raise ValueError("Изменение типа элемента с товара на категорию или с категории на товар не допускается")
        
        old_record.name = new_record.get("name")
        old_record.date = parsed_date

        update_parentId_if_needed(old_record, new_record, db)

        if old_record.type != ShopUnitType.category.value:
            if old_record.price != new_record.get("price"):
                log_price_changes(old_record, new_record.get("price"), parsed_date)
                old_record.price = new_record.get("price")

        db.session.commit()

        return True

    return False

def update_parentId_if_needed(old_record: ShopUnit, new_record: dict, db: SQLAlchemy):
    """
        В случае, если у объекта с базы и нового объекта разные parentId, то обновляем их, попутно удаляя 
        данный элемент из children старого родительского объекта и добавляя в children нового род. объекта
    """
    if old_record.parentId != new_record.get("parentId"):
        old_parent = ShopUnit.get_data_by_id(old_record.parentId)
        if old_parent:
            old_parent.children = [child for child in old_parent.children if child != old_record.id]
            db.session.commit()

        new_parent = ShopUnit.get_data_by_id(new_record.get("parentId"))
        if new_parent:
            new_parent.children = list(set([old_record.id] + new_parent.children))
            db.session.commit()

        old_record.parentId = new_record.get("parentId")

        db.session.commit()

def update_parent_date_if_needed(parentId: str, new_parsed_date: DateTime):
    """
        Обновляется дата у родительских объектов
    """
    parent = ShopUnit.get_data_by_id(parentId)
    if parent and parent.date != new_parsed_date:
        parent.date = new_parsed_date

        update_parent_date_if_needed(parent.parentId, new_parsed_date)

def check_for_duplicate_ids(data):
    """
        Проверка на дубликаты id в одном запросе
    """
    items = data.get("items")
    ids = [item["id"] for item in items]
    
    duplicates = [item for item, count in collections.Counter(ids).items() if count > 1]

    return True if duplicates else False

def validate_importing_unit(item: ShopUnit, parent: ShopUnit):
    """
        Валидация импортируемого объекта
    """
    if not item.get("name"):
        raise ValueError("Название элемента не может быть null")

    if item.get("type") == ShopUnitType.category.value and item.get("price"):
        raise ValueError("У категорий поле price должно содержать null")

    if parent and parent.type != "CATEGORY":
        raise ValueError("Родителем товара или категории может быть только категория")

def log_price_changes(shop_unit: ShopUnit, new_price: int, date: DateTime):
    """
        Сохраняю историю изменения цены на товары
    """
    if shop_unit.shop_unit_changes:
        history = shop_unit.shop_unit_changes 
        history.date_and_price = [{"price": new_price, "date": date}] + history.date_and_price
        shop_unit.shop_unit_changes = history
    else:
        price_changes = ShopUnitChanges()
        price_changes.date_and_price = [{"price": new_price, "date": date}]

        shop_unit.shop_unit_changes = price_changes
