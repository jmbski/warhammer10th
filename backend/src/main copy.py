import json
import datetime

from .services import Utils

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

# from .entities.data_model import DataModel, DataModelSchema
# from .entities.data_property import DataProperty, DataPropertySchema
from .entities.general_data import *

# from .services.database_service import *
from .services.DB_Service import *
from .services.Common import *
from requests import get

import pymysql


# creating the Flask application
app = Flask(__name__)
CORS(app, resources={r"/services/*": {"origins": "*"}})
# generate database schema
# Base.metadata.create_all(engine)

# start session
# session = Session()

# check for existing data
# exams = session.query(Exam).all()


"""_summary_
    TODO:
        improve on the status response capabilities
        make table selection modular
        
Returns:
    _type_: _description_
"""

env_props = "properties/environment.properties"


@app.route("/services/test")
def testData():
    return "This is a test"


@app.route("/services/checkUser", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def check_user():
    httpResponse = HTTPResponse(None)
    request_data = QueryRequest(request.get_json())
    """ engine = get_mysql_engine("properties/environment.properties")
    session = get_session(engine)
    Base.metadata.create_all(engine)
    cols = request_data.column_data
    print("cols" + str(cols))
    if cols is not None:
        filter = {}
        for col in cols:
            column = RequestColumn(col)
            filter[column.column_name] = column.value
        db_response = select_user(session, filter, debug=request_data.debug)
        httpResponse.data = {"userStatus": len(db_response) > 0} """

    return httpResponse.__dict__


@app.route("/services/registerUsername", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def register_user():
    httpResponse = HTTPResponse(None)
    request_data = request.get_json()
    """ engine = get_mysql_engine("properties/environment.properties")
    session = get_session(engine)
    Base.metadata.create_all(engine)
    username = request_data["username"]

    if username is not None:
        cols = []
        username_col = RequestColumn({"column_name": "username", "value": username})
        cols.append(username_col)
        if cols is not None:
            filter = {}
            for col in cols:
                filter[col.column_name] = col.value
            db_response = select_user(session, filter, debug=False)
            if len(db_response) > 0:
                httpResponse.data = "User exists"
                httpResponse.error_code = 5
            else:
                insert_values = {}
                passkey = generate_id()
                passkey_col = RequestColumn(
                    {"column_name": "passkey", "value": passkey}
                )
                cols.append(passkey_col)
                for col in cols:
                    insert_values[col.column_name] = col.value

                db_response = insert_user(session, insert_values, debug=True)
                if db_response["SQL status"] == "Row inserted successfully":
                    httpResponse.data = {"passkey": passkey}
                    httpResponse.status = 200
                else:
                    httpResponse.data = {"error": "Key error"}
                    httpResponse.error_code = 6
                    httpResponse.error_data = (
                        "Error occurred while trying to insert new user"
                    ) """

    return httpResponse.__dict__


@app.route("/services/dataRequest", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def process_request():
    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    print(cursor.fetchall())

    return ""


""" @app.route("/services/dataRequest_deprecated", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def process_request_deprecated():
    httpResponse = HTTPResponse(None)
    ip = get("https://api.ipify.org").content.decode("utf8")
    print("My public IP address is: {}".format(ip))
    print("Requested")
    request_data = QueryRequest(request.get_json())
    engine = get_mysql_engine("properties/environment.properties")
    session = get_session(engine)
    Base.metadata.create_all(engine)
    if request_data is not None:
        operation = str(request_data.operation).lower()
        # TODO: add WHERE clause
        cols = request_data.column_data
        if operation == "select":
            if cols is not None:
                filter = {}
                for col in cols:
                    column = RequestColumn(col)
                    filter[column.column_name] = column.value
                db_response = select_general_data(
                    session, filter, debug=request_data.debug
                )
                httpResponse.data = db_response

        if operation == "insert":
            insert_values = {}
            for col in cols:
                column = RequestColumn(col)
                insert_values[column.column_name] = column.value

            db_response = insert_general_data(
                session, insert_values, debug=request_data.debug
            )
            httpResponse.data = db_response

        if operation == "update":
            update_values = {}
            update_where = {}
            for col in cols:
                column = RequestColumn(col)
                update_values[column.column_name] = column.value

            for col in request_data.where:
                column = RequestColumn(col)
                update_where[column.column_name] = column.value

            db_response = update_general_data(
                session, update_values, update_where, debug=request_data.debug
            )
            httpResponse.data = db_response

        if operation == "delete":
            delete_where = {}

            for col in request_data.where:
                column = RequestColumn(col)
                delete_where[column.column_name] = column.value

            db_response = delete_general_data(
                session, delete_where, debug=request_data.debug
            )
            httpResponse.data = db_response
    session.close()

    return httpResponse.__dict__ """
