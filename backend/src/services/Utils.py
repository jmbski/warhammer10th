import json
import os


def init_by_json(object, init):
    if init is not None and isinstance(init, dict):
        for property, value in init.items():
            if hasattr(object, property):
                setattr(object, property, value)


def tuple_to_json(data: tuple, mapping: list):
    new_object = {}
    col = 0
    for value in data:
        prop_name = mapping[col]
        if isinstance(value, bytes):
            value = value.decode("utf-8").replace("'", '"')
        new_object[prop_name] = value
        col += 1
    return new_object


def remove_key_value_pair(dct, key):
    if key in dct:
        del dct[key]
    else:
        print("key not found")


def find_in_object_list(obj_list: list, target_prop: str, target_value):
    if obj_list is not None:
        for item in obj_list:
            print("item: " + str(item))
            print(hasattr(item, target_prop))
            print("trying class object")
            if hasattr(item, target_prop):
                if getattr(item, target_prop) == target_value:
                    print("item found")
                    return item
            elif item[target_prop] is not None and item[target_prop] == target_value:
                print("item found")
                return item

    return None
