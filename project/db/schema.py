from . import db

from sqlalchemy import ARRAY, Column, String
from enum import Enum

from sqlalchemy.dialects.postgresql import JSON

class ShopUnitType(str, Enum):
    offer = 'OFFER'
    category = 'CATEGORY'

class ShopUnitChanges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_unit_id = db.Column(db.String(128), db.ForeignKey('shop_unit.id'), nullable=False,)
    date_and_price = db.Column(JSON)

    @staticmethod
    def get_data_by_id(shop_unit_id: str):
        """
            Получение объекта из базы по заданному айди
        """
        return ShopUnitChanges.query.filter(ShopUnitChanges.shop_unit_id == shop_unit_id).first()

class ShopUnit(db.Model):
    id = db.Column(db.String(128), primary_key=True, nullable=False)
    name = db.Column(db.String(128))
    date = db.Column(db.DateTime, nullable = False)
    parentId = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    children = Column(ARRAY(String))
    shop_unit_changes = db.relationship('ShopUnitChanges', cascade="all, delete", backref='shop_unit', uselist=False)

    @staticmethod
    def get_data_by_id(id: str):
        """
            Получение объекта из базы по primary key
        """
        return ShopUnit.query.get(id)

    def as_dict(self):
        """
            Конвертирует объект в словарь, попутно форматируя дату в формат ISO-8601
        """
        d = {}
        for column in self.__table__.columns:
            d[column.name] = f"{getattr(self, column.name).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z" if column.name == "date" else getattr(self, column.name)
        return d