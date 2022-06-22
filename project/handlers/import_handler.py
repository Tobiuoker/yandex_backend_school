import collections
from typing import List
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import DateTime
from werkzeug import Request
from project.db.schema import ShopUnit, ShopUnitSchema
from flask import Flask, make_response

from project.handlers.util import parse_str_to_date

def import_handler(request: Request, db: SQLAlchemy, app: Flask):
    new_data_to_upload = []
    parents_date_to_update = []

    # for dictionary in request:
    #     if not dictionary:
    #         return make_response("Невалидная схема документа или входные данные не верны.", 400)
    #     parsed_date = f'{parse_str_to_date(dictionary.get("updateDate"))}' 

    #     for item in dictionary.get("items"):
    #         if item.get("parentId"):
    #             parent = ShopUnit.get_data_by_id(item.get("parentId"))
    #             if parent:
    #                 if parent.children:
    #                     app.logger.info("Aga1 %s", parent.children)
    #                     app.logger.info("Aga2 %s", item.get("id"))
    #                     parent.children = [item.get("id")] + parent.children
    #                 else:
    #                     parent.children = [item.get("id")]
    #                 db.session.commit()
                

    #         if not update_record_if_needed(item, db, parsed_date):
    #             new_data_to_upload += [parse_dict_to_shop_unit(item, parsed_date)]
            
    #         if item.get("parentId"):
    #             parents_date_to_update = [(item.get("parentId"), parsed_date)]
    

    if request.headers['content-type'] != 'application/json':
        raise ValidationError("Невалидная схема документа или входные данные не верны.")

    data = request.get_json()

    if check_for_duplicate_ids(data):
        raise ValidationError("В одном запросе не может быть двух элементов с одинаковым id")

    parsed_date = f'{parse_str_to_date(data.get("updateDate"))}' 

    for item in data.get("items"):
        parent = ShopUnit.get_data_by_id(item.get("parentId"))

        validate_importing_unit(item, parent)

        if not update_record_if_needed(item, parsed_date, db):
            db.session.add(parse_dict_to_shop_unit(item, parsed_date))

            if parent:
                if parent.children:
                    parent.children = list(set([item.get("id")] + parent.children))
                else:
                    parent.children = [item.get("id")]
                db.session.commit()
        
        if item.get("parentId"):
            parents_date_to_update += [(item.get("parentId"), parsed_date)]

    for (parentId, parsed_date) in parents_date_to_update:
        update_parent_date_if_needed(parentId, parsed_date)

    db.session.commit()

    return make_response("Вставка или обновление прошли успешно.", 200)

def parse_dict_to_shop_unit(data: dict, parsed_date: DateTime) -> ShopUnit:
    """
        Парсит словарь в модельку

        data: словарь с невалидированными данными
        parsed_date: форматированная дата вида "2022-02-02 12:00:00"

        return: спарсенную модельку типа ShopUnit
    """
    data["date"] = parsed_date
    schema = ShopUnitSchema()
    result = schema.load(data)
    
    return ShopUnit(**result)

def update_record_if_needed(new_record: ShopUnit, parsed_date: DateTime, db: SQLAlchemy) -> bool:
    """
        Обновляет данные, если они уже имеются в базе

        new_record: новое значение для строки с таким же айди
        db: объект базы данных

        return: bool значение (было ли произведено обновление)
    """
    old_record = ShopUnit.get_data_by_id(new_record["id"])

    if old_record:
        if old_record.type != new_record["type"]:
            raise ValidationError("Изменение типа элемента с товара на категорию или с категории на товар не допускается")
        
        old_record.name = new_record.get("name")
        old_record.date = parsed_date

        update_parentId_if_needed(old_record, new_record, db)

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
        raise ValidationError("Название элемента не может быть null")

    if item.get("type") == "CATEGORY" and item.get("price"):
        raise ValidationError("У категорий поле price должно содержать null")

    if parent and parent.type != "CATEGORY":
        raise ValidationError("Родителем товара или категории может быть только категория")