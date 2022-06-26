from datetime import timedelta
from typing import List
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from project.db.schema import ShopUnit

from project.handlers.util import parse_str_to_date, shop_unit_list_to_dict_list_without_children

def sales_handler(date: str, db: SQLAlchemy, app: Flask):
    """
        Получение элементов, цена которых была обновлена за последние 24 часа от времени переданном в запросе
    """

    parsed_date = parse_str_to_date(date)
    previous_day = parsed_date - timedelta(days=1)

    result = get_data_between_dates(previous_day, parsed_date, db)

    dict_result = shop_unit_list_to_dict_list_without_children(result)

    return make_response(jsonify(dict_result), 200) 

    
def get_data_between_dates(initial_date: DateTime, end_date: DateTime, db: SQLAlchemy) -> List[ShopUnit]:
    """
        Запрос в базу с промежутком времени, за который нужно достать данные
    """
    return db.session.query(ShopUnit).filter(ShopUnit.date >= initial_date, ShopUnit.date < end_date).all()
