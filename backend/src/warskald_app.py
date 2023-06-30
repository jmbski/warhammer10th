import json
import datetime

from .services import Utils

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

# from .entities.data_model import DataModel, DataModelSchema
# from .entities.data_property import DataProperty, DataPropertySchema
# from .entities.general_data import *

# from .services.database_service import *
from .services.DB_Service import *
from .services.Common import *
from requests import get

import pymysql


# creating the Flask application
app = Flask(__name__)
CORS(app, resources={r"/services/*": {"origins": "*"}})


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
    user = User(request.get_json())

    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )

    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM users WHERE username = '{user.username}' and passkey = '{user.passkey}';"
    )
    user_exists = len(cursor.fetchall()) > 0
    httpResponse.data = {"userStatus": user_exists}
    return httpResponse.__dict__


@app.route("/services/registerUsername", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def register_user():
    httpResponse = HTTPResponse(None)
    request_data = request.get_json()

    username = request_data["username"]
    if username is not None:
        connection_settings = ConnectionSettings(env_props)
        conn = pymysql.connect(
            user=connection_settings.user,
            passwd=connection_settings.password,
            host=connection_settings.host,
            db=connection_settings.dbname,
        )

        user_exists = check_user_exists(username, conn)

        if user_exists:
            httpResponse.error_code = 5
        else:
            passkey = generate_id()
            sql_request = QueryRequest(
                {
                    "table": "users",
                    "operation": "insert",
                    "column_data": [
                        {"column_name": "username", "value": username},
                        {"column_name": "passkey", "value": passkey},
                    ],
                }
            )
            db_response = handle_sql_request(sql_request, conn)
            # handle db_response
            if isinstance(db_response, str):  # meaning a failure, for now
                httpResponse.error_code = 7  # need to codify these
                httpResponse.error_data = db_response
            else:
                httpResponse.data = {"username": username, "passkey": passkey}
        conn.close()

    return httpResponse.__dict__


@app.route("/services/loadUserWorkspaces", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def load_user_workspaces():
    httpResponse = HTTPResponse(None)
    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )

    user = User(request.get_json())
    username = user.username
    if username is not None:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM general_data WHERE owning_user = '"
            + username
            + "' and object_type = 'dnd_workspace';"
        )
        data = cursor.fetchall()
        response_data = {}
        if isinstance(data, tuple):
            for item in data:
                data_item = tuple_to_json(item, general_data_props)
                response_data[data_item["id"]] = data_item

        httpResponse.data = response_data

    return httpResponse.__dict__


@app.route("/services/saveGeneralItem", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def save_item():
    httpResponse = HTTPResponse(None)
    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )

    request_data = GeneralDataItem(request.get_json())

    if request_data.id is None or request_data.id == "":
        registered_id = register_id(conn)
        request_data.id = registered_id
    if request_data.json_data is not None:
        if isinstance(request_data.json_data, str):
            json_data = json.loads(request_data.json_data)
            data_id = json_data["id"]
            if data_id == None or data_id == "":
                json_data["id"] = request_data.id
                request_data.json_data = json.dumps(json_data)

    query_data = QueryRequest(None)
    query_data.operation = "insert"
    query_data.column_data = []
    for prop, value in request_data.__dict__.items():
        query_data.column_data.append(
            RequestColumn({"column_name": prop, "value": value})
        )

    statement = build_sql_statement(query_data)
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    httpResponse.data = {"return": cursor.fetchall(), "id": request_data.id}

    return httpResponse.__dict__


@app.route("/services/removeItem", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def remove_item():
    httpResponse = HTTPResponse(None)
    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )
    request_data = QueryRequest(request.get_json())
    if request_data.where is not None:
        print("where exists" + str(request_data.where))
        delete_id = find_in_object_list(request_data.where, "column_name", "id")[
            "value"
        ]
        print("delete_id: " + str(delete_id))
        if delete_id is not None:
            try:
                print("attempting")
                query = build_sql_statement(request_data)
                cursor = conn.cursor()
                cursor.execute(query)
                print(cursor.fetchall())
                conn.commit()
                httpResponse.data["workspaceID"] = delete_id
            except Exception as inst:
                print(inst)

    return httpResponse.__dict__


@app.route("/services/dataRequest", methods=["POST"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def process_request():
    httpResponse = HTTPResponse(None)
    connection_settings = ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )

    request_data = QueryRequest(request.get_json())

    if request_data.column_data is not None:
        id_value = find_in_object_list(request_data.column_data, "column_name", "id")
        if id_value is not None:
            if str.lower(request_data.operation) == "insert":
                request_data.operation = "update"
        else:
            registered_id = register_id(conn)
            request_data.column_data.append(
                {"column_name": "id", "value": register_id(conn)}
            )

    httpResponse.data = handle_sql_request(request_data, conn)
    print("httpresponse:")
    print(httpResponse.data)
    if id_value is not None:
        httpResponse.data["id"] = id_value
    elif registered_id is not None:
        httpResponse.data["id"] = registered_id
    conn.close()

    return httpResponse.__dict__
