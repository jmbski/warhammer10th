import string
import random
from ..entities.general_data import (
    GeneralDataStructure,
    GeneralData,
    IDRegister,
    User,
    UserStructure,
)
from ..entities.entity import Base
from sqlalchemy import create_engine, insert, update, delete

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from .Utils import *
from pymysql.err import IntegrityError as pmsIntegrityError

max_retries = 3


class RequestColumn:
    column_name = None
    value = None
    conditional = None
    operator = None
    primary_key = None
    auto_increment = None
    foreign_key = None
    not_null = None

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)


class QueryJoin:
    join_type = None
    table = None
    join_columns = None
    where = None

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)


class SQLWhere:
    column_name = None
    value = None
    value_list = None
    conditional = None
    operator = None

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)


class QueryRequest:
    database = None
    operation = None
    table = None
    column_data = None
    where = None
    joins = None
    on_duplicate_key = None
    update_on_duplicate = None
    debug = False

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)


def get_mysql_engine(config_file):
    # Initialize a dictionary to store the connection settings
    connection_settings = {}

    # Read the config file
    config_file_data = open(config_file).readlines()

    # Extract the connection settings from the config file
    for line in config_file_data:
        if "DB_HOST" in line:
            connection_settings["host"] = line.split("=")[1].strip()
        elif "DB_PORT" in line:
            connection_settings["port"] = line.split("=")[1].strip()
        elif "DB_USER" in line:
            connection_settings["user"] = line.split("=")[1].strip()
        elif "DB_PASSWORD" in line:
            connection_settings["password"] = line.split("=")[1].strip()
        elif "DB_NAME" in line:
            connection_settings["dbname"] = line.split("=")[1].strip()

    db_host = connection_settings["host"]
    db_name = connection_settings["dbname"]
    db_user = connection_settings["user"]
    db_password = connection_settings["password"]
    db_port = connection_settings["port"]
    print(
        f"mysql+mysqlconnector://"
        + db_user
        + ":"
        + db_password
        + "@"
        + db_host
        + ":"
        + db_port
        + "/"
        + db_name
    )
    # engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    engine = create_engine(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    # mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
    # mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
    # Return the connection settings
    return engine


def get_session(engine=None, config_file=None):
    Session = {}
    session = {}
    if engine is not None:
        Session = sessionmaker(bind=engine)
    elif config_file is not None:
        engine = get_mysql_engine(config_file)
        Session = sessionmaker(bind=engine)
    if Session is not {}:
        session = Session()
    return session


def select_user(session, filter, debug=False):
    query = session.query(User)

    if isinstance(filter, dict):
        for property, value in filter.items():
            if hasattr(User, property):
                query = query.filter_by(**{property: value})

    data = query.all()
    structure = UserStructure()
    converted_data = []
    for datum in data:
        cleansed_datum = {}
        for property, value in datum.__dict__.items():
            if hasattr(datum, property):
                if hasattr(structure, property) and isinstance(
                    structure.__dict__[property], dict
                ):
                    value = json.loads(value)
                cleansed_datum[property] = value
        data_object = UserStructure(cleansed_datum)
        datum_json = json.dumps(
            data_object.__dict__, indent=4, sort_keys=True, default=str
        )
        converted_data.append(datum_json)
    session.close()
    return converted_data


def insert_user(session, insert_values, update_on_duplicate=True, debug=False):
    statement = insert(User)
    can_execute = True
    response = "Command not executed"
    if debug:
        print("creating insert for values: " + str(insert_values))

    if isinstance(insert_values, dict):
        userData = UserStructure(insert_values)
        for column, value in insert_values.items():
            if hasattr(userData, column) and column != "id":
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.values(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.values(**{column: value})

        if "id" not in insert_values:
            id_str = generate_id()
        else:
            id_str = insert_values["id"]

        id_exists = check_id_exists(session, id_str, debug=debug)
        if id_exists and update_on_duplicate == True:
            update_where = {"id": id_str}
            remove_key_value_pair(insert_values, "id")
            return update_user_data(session, insert_values, update_where, debug=debug)
        elif id_exists and update_on_duplicate == False:
            return "Cannot insert due to duplicate key"
        else:
            registered_id = register_id(session, id_str, debug=debug)

            if registered_id is not None and isinstance(registered_id, str):
                statement = statement.values(id=registered_id)
                return execute_insert(session, statement, insert_values, debug=debug)

    return response


def update_user_data(session, update_values, update_where, debug=False):
    statement = update(User)
    userData = UserStructure(None)
    if debug:
        print("Running update for:\n")
        print("Values: " + str(update_values))
        print("Where: " + str(update_where))

    if isinstance(update_values, dict):
        for column, value in update_values.items():
            if hasattr(userData, column):
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.values(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.values(**{column: value})

    if isinstance(update_where, dict):
        for column, value in update_where.items():
            if hasattr(userData, column):
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.filter_by(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.filter_by(**{column: value})

    response = session.execute(statement)

    return {"updated_rows": response.rowcount}


def select_general_data(session, filter, debug=False):
    query = session.query(GeneralData)

    if isinstance(filter, dict):
        for property, value in filter.items():
            if hasattr(GeneralData, property):
                query = query.filter_by(**{property: value})

    data = query.all()
    structure = GeneralDataStructure()
    converted_data = []
    for datum in data:
        cleansed_datum = {}
        for property, value in datum.__dict__.items():
            if hasattr(datum, property):
                if hasattr(structure, property) and isinstance(
                    structure.__dict__[property], dict
                ):
                    value = json.loads(value)
                cleansed_datum[property] = value
        data_object = GeneralDataStructure(cleansed_datum)
        datum_json = json.dumps(
            data_object.__dict__, indent=4, sort_keys=True, default=str
        )
        converted_data.append(datum_json)
    session.close()
    return converted_data


def execute_insert(session, statement, insert_values, count=0, debug=False):
    count += 1
    can_execute = True
    if debug:
        print("executing insert statement: " + str(statement))
        print("attempt: " + str(count))

    if count > max_retries:
        can_execute = False

    if can_execute:
        if isinstance(insert_values, dict) and "id" not in insert_values:
            if debug:
                print("from execute")
            insert_values["id"] = register_id(session, debug=debug)
            statement = statement.values(id=insert_values["id"])

        try:
            session.execute(statement)
            return {
                "SQL status": "Row inserted successfully",
                "id": insert_values["id"],
                "response_status": 0,
            }

        except IntegrityError as inst:
            if "Duplicate entry" in str(inst.orig):
                print("Duplicate key error")
                remove_key_value_pair(insert_values, "id")

                return execute_insert(
                    session, statement, insert_values, count=count, debug=debug
                )

            else:
                response = {
                    "SQL status": "Unknown integrity error, row not inserted",
                    "id": None,
                    "response_status": 3,
                }
                if debug == True:
                    print("Non duplicate error: " + str(response))
                return response

        except Exception as inst:
            if debug == True:
                print("Unknown SQL error:\n" + str(inst))
            return {
                "SQL status": "Unknown SQL error, row not inserted",
                "id": None,
                "response_status": 2,
            }


def insert_general_data(session, insert_values, update_on_duplicate=True, debug=False):
    statement = insert(GeneralData)
    can_execute = True
    response = "Command not executed"
    if debug:
        print("creating insert for values: " + str(insert_values))

    if isinstance(insert_values, dict):
        generalData = GeneralDataStructure(insert_values)
        for column, value in insert_values.items():
            if hasattr(generalData, column) and column != "id":
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.values(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.values(**{column: value})

        if "id" not in insert_values:
            id_str = generate_id()
        else:
            id_str = insert_values["id"]

        id_exists = check_id_exists(session, id_str, debug=debug)
        if id_exists and update_on_duplicate == True:
            update_where = {"id": id_str}
            remove_key_value_pair(insert_values, "id")
            return update_general_data(
                session, insert_values, update_where, debug=debug
            )
        elif id_exists and update_on_duplicate == False:
            return "Cannot insert due to duplicate key"
        else:
            registered_id = register_id(session, id_str, debug=debug)
            if debug == True:
                print("registered id: " + registered_id)
            if registered_id is not None and isinstance(registered_id, str):
                statement = statement.values(id=registered_id)
                if debug == True:
                    print(statement)
                return execute_insert(session, statement, insert_values, debug=debug)

    return response


def update_general_data(session, update_values, update_where, debug=False):
    statement = update(GeneralData)
    generalData = GeneralDataStructure(None)
    if debug:
        print("Running update for:\n")
        print("Values: " + str(update_values))
        print("Where: " + str(update_where))

    if isinstance(update_values, dict):
        for column, value in update_values.items():
            if hasattr(generalData, column):
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.values(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.values(**{column: value})

    if isinstance(update_where, dict):
        for column, value in update_where.items():
            if hasattr(generalData, column):
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.filter_by(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.filter_by(**{column: value})

    response = session.execute(statement)
    response_status = 0
    if response.rowcount <= 0:
        response_status = 1
    return {"updated_rows": response.rowcount, "response_status": response_status}


def delete_general_data(session, delete_where, debug=False):
    statement = delete(GeneralData)
    generalData = GeneralDataStructure(None)

    if isinstance(delete_where, dict):
        for column, value in delete_where.items():
            if hasattr(generalData, column):
                if isinstance(value, dict) or isinstance(value, list):
                    statement = statement.filter_by(
                        **{column: bytes(json.dumps(value), "utf8")}
                    )
                else:
                    statement = statement.filter_by(**{column: value})

    response = session.execute(statement)

    return {"deleted_rows": response.rowcount}


def generate_id():
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for i in range(32))


def check_id_exists(session, id_str, debug=False) -> bool:
    if session is not None and id_str is not None and isinstance(id_str, str):
        if debug:
            print("Checking existence of id: " + str(id_str))

        statement = session.query(IDRegister).filter_by(id=id_str)
        results = statement.all()
        return len(results) > 0

    return False


def register_id(session, id_str=None, debug=False) -> str:
    registered_id = None
    count = 0
    if debug:
        print("Executing register_id")

    while (
        registered_id is None or not isinstance(registered_id, str)
    ) and count < max_retries:
        if id_str is None:
            id_str = generate_id()

        statement = insert(IDRegister).values(id=id_str)
        registered_id = execute_insert(session, statement, {"id": id_str}, debug=debug)[
            "id"
        ]
        count += 1
        if debug:
            print("looping in while")
            print("count: " + str(count))

    return registered_id
