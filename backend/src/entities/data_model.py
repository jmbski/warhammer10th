# coding=utf-8

from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .entity import Entity, Base


class DataModel(Entity, Base):
    __tablename__ = 'data_models'

    created_by = Column(String)

    def __init__(self, datum_name, created_by):
        Entity.__init__(self, datum_name)
        self.created_by = created_by
        

class DataModelSchema(Schema):
    id = fields.Number()
    datum_name = fields.Str()
    created_by = fields.Str()