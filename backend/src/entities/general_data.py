# coding=utf-8
import json
import datetime
from sqlalchemy import Column, String, DateTime, BLOB, BigInteger
from marshmallow import Schema, fields
from .entity import Entity, Base, EntityIntID


class IDRegister(Entity, Base):
    __tablename__ = "id_registry"

    def __init__(self):
        super().__init__()


class User(Entity, Base):
    __tablename__ = "users"

    username = Column(String)
    email = Column(String)
    passkey = Column(String)

    def __init__(self, init) -> None:
        if init is not None and isinstance(init, dict):
            for property, value in init.items():
                if hasattr(self, property):
                    setattr(self, property, value)
        Entity.__init__(self)


class GeneralData(Entity, Base):
    __tablename__ = "general_data"

    created_by = Column(String)
    last_updated_by = Column(String)
    creation_date = Column(DateTime)
    last_update_date = Column(DateTime)
    object_type = Column(String)
    datum_name = Column(String)
    json_data = Column(BLOB)

    def __init__(self, init) -> None:
        if init is not None and isinstance(init, dict):
            for property, value in init.items():
                if hasattr(self, property):
                    setattr(self, property, value)
        Entity.__init__(self)


class GeneralDataStructure:
    id = ""
    created_by = ""
    last_updated_by = ""
    creation_date = None
    last_update_date = None
    object_type = ""
    datum_name = ""
    json_data = {}

    def __init__(self, init=None) -> None:
        if init is not None and isinstance(init, dict):
            for property, value in init.items():
                if hasattr(self, property):
                    setattr(self, property, value)

        else:
            self.id = ""
            self.created_by = ""
            self.last_updated_by = ""
            self.creation_date = datetime.date.today()
            self.last_update_date = datetime.date.today()
            self.object_type = ""
            self.datum_name = ""
            self.json_data = {}

    def __iter__(self):
        yield from {
            "id": self.id,
            "created_by": self.created_by,
            "last_updated_by": self.last_updated_by,
            "creation_date": self.creation_date,
            "last_update_date": self.last_update_date,
            "object_type": self.object_type,
            "datum_name": self.datum_name,
            "json_data": self.json_data,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()


class UserStructure:
    id = ""
    username = ""
    passkey = ""
    email = ""

    def __init__(self, init=None) -> None:
        if init is not None and isinstance(init, dict):
            for property, value in init.items():
                if hasattr(self, property):
                    setattr(self, property, value)

        else:
            self.id = ""
            self.username = ""
            self.passkey = ""
            self.email = ""

    def __iter__(self):
        yield from {
            "id": self.id,
            "username": self.username,
            "passkey": self.passkey,
            "email": self.email,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()


class GeneralDataSchema(Schema):
    id = fields.Str()
    created_by = fields.Str()
    last_updated_by = fields.Str()
    datum_name = fields.Str()
    creation_date = fields.DateTime()
    last_update_date = fields.DateTime()
    object_type = fields.Str()
    json_data = fields.Mapping()
