from datetime import datetime
from typing import List
from dateutil.parser import parse
from project.db.schema import ShopUnit

def parse_str_to_date(strdate):
    """
        Парсит строку с датой вида 2022-02-02T12:00:00.000Z в формат datetime
    """
    return datetime.strptime(str(parse(strdate))[:-6], "%Y-%m-%d %H:%M:%S")

def shop_unit_list_to_dict_list(data: List[ShopUnit]) -> List[dict]:
    """
        Превращает массив объектов ShopUnit в массив словарей
    """
    return list(map(ShopUnit.as_dict, data))