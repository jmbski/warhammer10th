from .Utils import *


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
    database = "warskald_main"
    operation = "select"
    table = "general_data"
    column_data = None
    where = None
    joins = None
    on_duplicate_key = None
    update_on_duplicate = None
    debug = False

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)


class ConnectionSettings:
    host = ""
    port = ""
    user = ""
    password = ""
    dbname = ""

    def __init__(self, env_props=None) -> None:
        # Read the config file
        config_file_data = open(env_props).readlines()

        # Extract the connection settings from the config file
        for line in config_file_data:
            if "DB_HOST" in line:
                self.host = line.split("=")[1].strip()
            elif "DB_PORT" in line:
                self.port = line.split("=")[1].strip()
            elif "DB_USER" in line:
                self.user = line.split("=")[1].strip()
            elif "DB_PASSWORD" in line:
                self.password = line.split("=")[1].strip()
            elif "DB_NAME" in line:
                self.dbname = line.split("=")[1].strip()


class User:
    username = ""
    passkey = ""
    email = ""

    def __init__(self, init=None) -> None:
        init_by_json(self, init)


class GeneralDataItem:
    id: str = None
    created_by: str = ""
    owning_user: str = ""
    last_updated_by: str = ""
    creation_date = None
    last_update_date = None
    object_type: str = ""
    datum_name: str = ""
    json_data: dict = ""

    def __init__(self, init=None) -> None:
        init_by_json(self, init)


general_data_props = [
    "id",
    "created_by",
    "owning_user",
    "last_updated_by",
    "creation_date",
    "last_update_date",
    "object_type",
    "datum_name",
    "json_data",
]
