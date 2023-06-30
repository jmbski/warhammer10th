# Importing libs
from PIL import Image
import pytesseract


class Test:
    test = "test"

    def __init__(self, test="") -> None:
        self.test = test


def d_hasattr(obj: dict, property: str) -> bool:
    if property in obj.keys():
        return True
    else:
        return False


def d_setattr(obj: dict, property: str, value) -> None:
    obj[property] = value


def d_getattr(obj: dict, property: str):
    if d_hasattr(obj, property):
        return obj[property]
    return None


def find_in_object_list(property: str, value, items: list):
    result = None
    for item in items:
        try:
            if hasattr(item, property):
                prop = getattr(item, property)
                if prop == value:
                    result = item
            if result == None:
                raise Exception
        except Exception as inst:
            try:
                if item[property] == value:
                    result = item
            except Exception as inst:
                pass
    return result


obj = {"test": "test1", "test2": True}

d_setattr(obj, "test3", "kldsajglk")
print(obj)
