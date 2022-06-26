
from project.db.schema import ShopUnit

from flask import Flask, abort, jsonify, make_response

from dateutil.parser import parse

from copy import copy

from project.handlers.util import parse_str_to_date, shop_unit_list_to_dict_list_without_children

def get_statistics(id: str, from_date: str, to_date: str, app: Flask):
    """
        Статистика изменения цены за определенный промежуток времени
    """
    from_date_formatted = parse_str_to_date(from_date)
    to_date_formatted = parse_str_to_date(to_date)

    if from_date_formatted > to_date_formatted:
        raise ValueError("Некорректный формат запроса или некорректные даты интервала.")

    shop_unit = ShopUnit.get_data_by_id(id)

    if not shop_unit:
        abort(404)

    price_changes_history = shop_unit.shop_unit_changes.date_and_price

    price_changes_history_filtered = [x for x in price_changes_history if parse(x["date"]) > from_date_formatted and parse(x["date"])  < to_date_formatted]

    result = []
    for i in price_changes_history_filtered:
        temp = copy(shop_unit)
        temp.price = i.get("price")
        temp.date = parse(i.get("date"))
        result += [temp]

    return make_response(jsonify(shop_unit_list_to_dict_list_without_children(result)), 200) 