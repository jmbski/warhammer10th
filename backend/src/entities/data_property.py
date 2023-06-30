# coding=utf-8

from sqlalchemy import Column, String, Integer
from marshmallow import Schema, fields
from .entity import Entity, Base


class DataProperty(Entity, Base):
    __tablename__ = 'data_properties'

    type_id = Column(Integer)
    default_value = Column(String)
    current_value = Column(String)

    def __init__(self, type_id, default_value, current_value, datum_name):
        Entity.__init__(self, datum_name)
        self.type_id = type_id
        self.default_value = default_value
        self.current_value = current_value
        

class DataPropertySchema(Schema):
    id = fields.Number()
    datum_name = fields.Str()
    type_id = fields.Number()
    default_value = fields.Str()
    current_value = fields.Str()