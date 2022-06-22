from email.policy import strict
import marshmallow
from . import db

from marshmallow import Schema
from marshmallow.fields import Int, Str

from marshmallow.validate import Length, OneOf, Range

from sqlalchemy import ARRAY, Column, String
from enum import Enum

class ShopUnitType(str, Enum):
    offer = 'OFFER'
    category = 'CATEGORY'

class ShopUnit(db.Model):
    id = db.Column(db.String(128), primary_key=True, nullable=False)
    name = db.Column(db.String(128))
    date = db.Column(db.DateTime, nullable = False)
    parentId = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    children = Column(ARRAY(String))

    @staticmethod
    def get_data_by_id(id: str):
        """
            Получение объекта из базы по заданному айди
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

class ShopUnitSchema(Schema):
    id = Str(validate=Length(min=36, max=36), required=True, metadata={'index': True})
    name = Str(validate=Length(min=1, max=256),required=True)
    date = marshmallow.fields.DateTime()
    parentId = Str(validate=Length(min=36, max=36), allow_none=True)
    type = Str(validate=OneOf([unitType.value for unitType in ShopUnitType]), required=True)
    price = Int(validate=Range(min=0), strict=True)
    children = marshmallow.fields.List(marshmallow.fields.String())

    # class Meta:
    #     strict = True

    # @marshmallow.validates_schema
    # def validate(self, data, **kwargs):
    #     if data["type"] == "CATEGORY" and data.get("price"):
    #         raise ValidationError("У категорий поле price должно содержать null")
         
    #     if data["type"] != "CATEGORY" and data.get("children"):
    #         raise ValidationError("Родителем товара или категории может быть только категория")