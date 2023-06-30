import json


class DataSheet:
    unit_name: str = ""
    keywords: dict = {}
    ranged_weapons: dict = {}
    melee_weapons: dict = {}
    faction_keywords: list = []
    core_abilities: list = []
    faction_abilities: list = []
    unit_abilities: dict = {}
    invulnerable_save = 0
    composition = ""
    points = 0
    wargear_abilities = {}
    wargear_options = []
    leader = []
    equipped_with = ""
    profiles = {}
    issue_flag = False
    army_name = ""

    def __init__(self) -> None:
        self.unit_name: str = ""
        self.keywords: list = {}
        self.ranged_weapons: dict = {}
        self.melee_weapons: dict = {}
        self.faction_keywords: list = []
        self.core_abilities: list = []
        self.faction_abilities: list = []
        self.unit_abilities: dict = {}
        self.invulnerable_save = 0
        self.composition = ""
        self.points = {}
        self.wargear_abilities = {}
        self.wargear_options = []
        self.leader = []
        self.equipped_with = ""
        self.profiles = {}
        self.issue_flag = False
        self.army_name = ""

    def toJson(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
        )

    def toDict(self):
        self_dict = {}
        for property, value in self.__dict__.items():
            self_dict[property] = value
        return self_dict


class UnitComposition:
    unit_name = ""
    points = {}

    def __init__(self) -> None:
        self.unit_name = ""
        self.points = {}

    def toJson(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
        )

    def toDict(self):
        self_dict = {}
        for property, value in self.__dict__.items():
            self_dict[property] = value
        return self_dict


class Profile:
    movement = ""
    toughness = 0
    sv = ""
    wounds = 0
    leadership = ""
    objective_control = 0

    def __init__(self) -> None:
        self.movement = ""
        self.toughness = 0
        self.sv = ""
        self.wounds = 0
        self.leadership = ""
        self.objective_control = 0

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def toDict(self):
        self_dict = {}
        for property, value in self.__dict__.items():
            self_dict[property] = value
        return self_dict


class Weapon:
    category: str = ""
    name: str = ""
    weapon_range = 0
    attacks: int = 0
    ws: str = ""
    bs: str = ""
    strength: int = 0
    ap: int = 0
    damage: str = ""
    core_rules = []

    def __init__(self) -> None:
        self.category: str = ""
        self.name: str = ""
        self.weapon_range = 0
        self.attacks: int = 0
        self.ws: str = ""
        self.bs: str = ""
        self.strength: int = 0
        self.ap: int = 0
        self.damage: str = ""
        self.core_rules = []

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def toDict(self):
        self_dict = {}
        for property, value in self.__dict__.items():
            self_dict[property] = value
        return self_dict
