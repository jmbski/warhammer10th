import json
import os
import string, random
from pymysql import *
from .DataTypes import *


def build_sql_statement(request: QueryRequest):
    statement = ""

    # SELECT * FROM general_data;

    op_str = ""
    from_str = ""
    where_str = ""
    join_str = ""
    columns_str = ""
    column_values_str = ""
    update_values_str = ""

    cols = request.column_data

    if cols is not None:
        for col in cols:
            if isinstance(col, RequestColumn):
                columns_str += col.column_name + ","
                column_values_str += "'" + str(col.value) + "',"
                update_values_str += col.column_name + " = '" + str(col.value) + "',"
        columns_str = columns_str[0:-1]
        column_values_str = column_values_str[0:-1]
        update_values_str = update_values_str[0:-1]

    if request.table != None:
        from_str = request.database + "." + request.table + " "

    if request.where != None:
        for col in request.where:
            where_str += col["column_name"] + " = '" + col["value"] + "' and "
        where_str = where_str[0:-5]

    if request.joins != None:
        # build joins
        pass

    # assemble
    op = str.lower(request.operation)
    if op != None:
        op = str.lower(op)
        if op == "select":
            statement += "SELECT "
            if request.column_data is not None:
                statement += columns_str
            else:
                statement += " * "

            statement += from_str + " " + where_str

        if op == "insert":
            statement += (
                "INSERT INTO "
                + from_str
                + " ("
                + columns_str
                + ") VALUES ("
                + column_values_str
                + ") ON DUPLICATE KEY UPDATE "
                + update_values_str
            )

        if op == "update":
            statement = (
                "UPDATE "
                + from_str
                + " SET "
                + update_values_str
                + " WHERE "
                + where_str
            )

        if op == "delete":
            statement = "DELETE FROM " + from_str + " WHERE " + where_str

    return statement


def handle_sql_request(request: QueryRequest, conn: Connection):
    statement = ""
    response_data = None

    # SELECT * FROM general_data;
    op = str.lower(request.operation)
    item_id = find_in_object_list(request.column_data, "column_name", "id")

    op_str = ""
    from_str = ""
    where_str = ""
    join_str = ""
    columns_str = ""
    column_values_str = ""
    update_values_str = ""

    cols = request.column_data

    if cols is not None:
        for col in cols:
            # if isinstance(col, RequestColumn):
            columns_str += col["column_name"] + ","
            column_values_str += "'" + col["value"] + "',"
            update_values_str += col["column_name"] + " = '" + col["value"] + "',"
        columns_str = columns_str[0:-1]
        column_values_str = column_values_str[0:-1]
        update_values_str = update_values_str[0:-1]

    if request.table != None:
        from_str = request.database + "." + request.table + " "

    print(request.where)
    if request.where != None:
        for col in request.where:
            where_str += col["column_name"] + " = '" + col["value"] + "' and "
            print("col:")
            print(col)
        where_str = where_str[0:-5]

    if request.joins != None:
        # build joins
        pass

    # assemble
    cursor = conn.cursor()

    if op != None:
        op = str.lower(op)
        if op == "select":
            statement += "SELECT "
            if request.column_data is not None:
                statement += columns_str
            else:
                statement += " * "

            statement += from_str + " " + where_str

            cursor.execute(statement)
            response_data = cursor.fetchall()

        if op == "insert":
            statement += (
                "INSERT INTO "
                + from_str
                + " ("
                + columns_str
                + ") VALUES ("
                + column_values_str
                + ") ON DUPLICATE KEY UPDATE "
                + update_values_str
            )

            try:
                cursor.execute(statement)
                conn.commit()
                response_data = {"id": item_id}
            except Exception as inst:
                print("Error occurred trying to insert data")
                print(inst)
                response_data = "Error during insert"

        if op == "update":
            statement = (
                "UPDATE "
                + from_str
                + " SET "
                + update_values_str
                + " WHERE "
                + where_str
            )

            print("updating")
            print(statement)
            cursor.execute(statement)
            conn.commit()
            response_data = {"rowsAffected": cursor.fetchall()}

        if op == "delete":
            statement = "DELETE FROM " + from_str + " WHERE " + where_str
            response_data = {"rowsAffected": cursor.fetchall()}

    return response_data


def generate_id():
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for i in range(32))


def check_id_exists(session, id_str, debug=False) -> bool:
    pass
    """ if session is not None and id_str is not None and isinstance(id_str, str):
        if debug:
            print("Checking existence of id: " + str(id_str))

        statement = session.query(IDRegister).filter_by(id=id_str)
        results = statement.all()
        return len(results) > 0

    return False """


def register_id(conn: Connection, id_str=None, debug=False) -> str or None:
    registered_id = None
    count = 0
    if debug:
        print("Executing register_id")

    max_retries = 3

    while (
        registered_id is None or not isinstance(registered_id, str)
    ) and count < max_retries:
        if id_str is None:
            id_str = generate_id()

        statement = (
            "INSERT INTO warskald_main.id_registry (id) VALUES ('" + id_str + "');"
        )

        registered_id = ""
        cursor = conn.cursor()
        # print(cursor.mogrify(statement))
        try:
            print("adding new id")
            cursor.execute(statement)
            conn.commit()
            return id_str
        except Exception as inst:
            print(inst)

        count += 1
        if debug:
            print("looping in while")
            print("count: " + str(count))

    return None


def check_user_exists(username: str, conn: Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "';")
    data = cursor.fetchall()
    return len(data) > 0
