# coding=utf-8

from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector

# engine = get_mysql_engine("properties\environment.properties")


# Connect to the database

# def getMySql():
# Create a cursor
# mycursor = mydb.cursor()

# Execute a query
# mycursor.execute("SELECT * FROM data_objects")

# Fetch all the records
# result = mycursor.fetchall()

# Print the results
# for x in result:
# print(x)

# getMySql()

Base = declarative_base()


class Entity:
    id = Column(String, primary_key=True)

    def __init__(self, datum_name=None):
        pass


class EntityIntID:
    id = Column(Integer, primary_key=True)

    def __init__(self, datum_name=None):
        pass
