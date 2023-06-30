import pdfreader, os, json, subprocess, re, random
from PIL import Image, ImageChops, ImageEnhance
import pytesseract, pymysql

from pdfreader import PDFDocument, SimplePDFViewer
import packages.Classes as C
import packages.DB_Service as DB

crons = "./pdfs/necrons.pdf"
points = "./pdfs/points.pdf"
fd = open(crons, "rb")
viewer = SimplePDFViewer(fd)

_fd = open(points, "rb")
_viewer = SimplePDFViewer(_fd)
_viewer.navigate(1)
_viewer.render()
strs = _viewer.canvas.strings
plain_text = "".join(strs)
# print(plain_text)


def find_in_str_list(keyword: str, values: list) -> bool:
    for word in values:
        if keyword in word:
            return True
    return False


weapon_profile = "RANGEABSSAPD"
ranged_keyword = "RANGED WEAPONSRANGEABSSAPD"
melee_keyword = "MELEE WEAPONSRANGEAWSSAPD"


def parse_keywords(current_word: str, data_sheet: C.DataSheet, property: str):
    keywords = current_word.split(",")
    stripped_keywords = []
    for keyword in keywords:
        stripped_keywords.append(keyword.strip())

    if data_sheet is not None and hasattr(data_sheet, property):
        setattr(data_sheet, property, stripped_keywords)


def try_int(value):
    result = None
    try:
        result = int(value)
    except Exception as inst:
        result = value
    return result


def parse_weapon(weapon_strs: list, category: str):
    weapon = C.Weapon()
    weapon.category = category
    name_finished = False
    core_rules_open = False
    core_rules = ""
    range_complete = False
    index = 0
    na_range = ""

    strs_index = 0
    for string in weapon_strs:
        if (
            name_finished == False
            and "[" not in string
            and '"' not in string
            and "M" not in string
        ):
            weapon.name += string
        else:
            name_finished = True
            weapon.name = weapon.name.strip()
        if "[" in string:
            core_rules_open = True
        if core_rules_open:
            core_rules += string
        if "]" in string:
            core_rules_open = False

        if range_complete == True and weapon.weapon_range:
            if string != "/A":
                if index == 0:
                    weapon.attacks = try_int(string)
                elif index == 1:
                    if string == "N":
                        string = "N/A"
                    if category == "melee":
                        weapon.ws = string
                    else:
                        weapon.bs = string
                elif index == 2:
                    weapon.strength = try_int(string)
                elif index == 3:
                    weapon.ap = try_int(string)
                elif index == 4:
                    weapon.damage = string
                index += 1

        if '"' in string or string == "Melee":
            weapon.weapon_range = string
            range_complete = True
        strs_index += 1

    raw_core_rules = core_rules.replace("[", "").replace("]", "").split(",")
    if len(raw_core_rules) > 0:
        weapon.core_rules = []
        for rule in raw_core_rules:
            formatted_str = rule.strip()
            if formatted_str != "":
                weapon.core_rules.append(formatted_str)
    return weapon


def parse_abilities(abilities: list):
    abilities_dict = {}
    for ability in abilities:
        search_term = re.search("^[A-Z][a-zA-Z ]+\:", ability)
        if search_term is not None:
            term_group = search_term.group()
            if term_group is not None:
                ability_name = search_term.group().replace(":", "")
                ability_value = ability.replace(term_group, "").strip()
                abilities_dict[ability_name] = ability_value
    return abilities_dict


def parse_options(text: str, regex: str, separator="■"):
    search_term = re.search(regex, text)
    options = None
    if search_term is not None:
        options_str = search_term.groups()[0]
        raw_options = options_str.strip().split(separator)
        options = []
        for option in raw_options:
            if option.strip() != "":
                options.append(option.strip())

    return options


data_sheets = []


def find_data_sheet_by_name(unit_name: str, _data_sheets: list) -> C.DataSheet or None:
    for sheet in _data_sheets:
        if isinstance(sheet, C.DataSheet):
            if sheet.unit_name.lower() == unit_name.lower():
                return sheet

    return None


def find_stat_profiles(strings, unit_name):
    index = 0
    start_idx = 0
    matches = 0
    profiles = {}
    # print(strings)
    profile_title = unit_name
    profile_stats = ["M", "T", "SV", "W", "LD", "OC"]
    for string in strings:
        if string == profile_stats[matches]:
            matches += 1
        else:
            matches = 0
        if matches == 6:
            start_idx = index + 1
            break
        index += 1
    remaining_strs = strings[start_idx:]
    text = "".join(remaining_strs)
    search_term = re.search(".+?\+[0-9]([A-Z].*)", text)
    if search_term is not None and search_term.groups() is not None:
        profile_title = search_term.groups()[0]

    profile = C.Profile()
    index = 0
    profile_count = 1
    for value in remaining_strs:
        search_term = re.match("[a-z]|[A-Z]", value)

        # if we reach the defined end of a profile but there's still more valid profiles, they will be each added with an appended profile count
        if index == 6 and search_term is not None:
            profiles[profile_title + "_" + str(profile_count)] = profile.__dict__
            profile = C.Profile()
            index = 0
            profile_count += 1

        if search_term is None:
            if index == 0:
                profile.movement = value
            elif index == 1:
                profile.toughness = try_int(value)
            elif index == 2:
                profile.sv = value
            elif index == 3:
                profile.wounds = try_int(value)
            elif index == 4:
                profile.leadership = value
            elif index == 5:
                profile.objective_control = try_int(value)
            index += 1
    if profile_count == 1:
        profiles[profile_title] = profile.__dict__

    return profiles


known_faction_rules = []
army_rule = ""


def build_data_sheet(canvas_strings, previous_datasheet, army_rule=None) -> C.DataSheet:
    text_string = "".join(canvas_strings)  # .split(" ")
    raw_text = canvas_strings
    logging = False
    if "celestine" in text_string.lower():
        print(raw_text)
        logging = True
    data_sheet = C.DataSheet()
    data_sheet.ranged_weapons = {}
    data_sheet.melee_weapons = {}

    keywords_open = False
    faction_keywords_open = False

    ranged_strs = []
    ranged_open = False

    melee_strs = []
    melee_open = False

    weapon_strs = []
    weapon_open = False

    current_weapon = C.Weapon()

    # CORE:(.+?)[A-Z]{2} - core abilities
    # FACTION:(.+?[a-z])[A-Z] - faction abilities
    # (.*:)(.+?[\.])[A-Z] - unit abilities before last
    # ([A-Z].*:)( [A-Z].*)(INVULNERABLE SAVE\d\+|MTSVWLDOC5) - EOF
    num_count = 0  # used to count consecutive instances of numeric values to determine the end of a weapon profile
    if "ABILITIES" in text_string:
        current_word = ""
        for group in raw_text:
            if group != " ":
                current_word += group

            if ranged_open == True:
                ranged_strs.append(group)

            if melee_open == True:
                melee_strs.append(group)

            if (
                (melee_open == True or ranged_open == True)
                and weapon_open == False
                and re.match("[^0-9]*", group) is not None
            ):
                weapon_open = True
                weapon_strs = []

            if weapon_open == True:
                weapon_strs.append(group)

            if re.match("[d|D][0-9]*", group) and len(group.strip()) > 1:
                num_count += 1
            else:
                try:
                    num_val = int(group)
                    num_count += 1
                except Exception as inst:
                    num_count = 0

            if num_count == 3:
                weapon_open = False
                weapon_str = "".join(weapon_strs)
                current_word = current_word.replace(weapon_str, "")
                weapon_category = "ranged"
                if melee_open == True:
                    weapon_category = "melee"

                current_weapon = parse_weapon(weapon_strs, weapon_category)
                if current_weapon is not None:
                    if current_weapon.category == "melee":
                        data_sheet.melee_weapons[
                            current_weapon.name
                        ] = current_weapon.toDict()
                    else:
                        data_sheet.ranged_weapons[
                            current_weapon.name
                        ] = current_weapon.toDict()
            name_search = re.search(r"(.+?)KEYWORDS", current_word)
            if name_search is not None and data_sheet.unit_name == "":
                data_sheet.unit_name = name_search.groups()[0]
                current_word = current_word.replace(data_sheet.unit_name, "")
            keyword_search = re.search(r"(KEYWORDS)(?=:| – )", current_word)
            faction_keyword_search = re.search(
                r"(FACTION KEYWORDS)(?=:| – )", current_word
            )
            if keyword_search is not None and faction_keyword_search is not None:
                keywords_search = re.search(
                    r"KEYWORDS(.+?[a-z])(?=FACTION|[A-Z])", current_word
                )

                if keywords_search is not None:
                    current_word.replace(keywords_search.group(), "")
                    keywords_str = keywords_search.groups()[0]
                    if keywords_str.startswith(":"):
                        keywords = clean_list(keywords_str, ",", [":"])
                        if keywords is not None and len(keywords) > 0:
                            data_sheet.keywords[data_sheet.unit_name] = keywords
                    else:
                        keywords_str = keywords_str.replace(" – ", "")
                        keywords_str += "!@#"
                        multi_search = re.search(
                            r"(.+?):(.+?)(?=[A-Z][A-Z]|!@#)", keywords_str
                        )

                        while multi_search is not None:
                            full_text = multi_search.group()
                            groups = multi_search.groups()
                            if len(groups) == 2:
                                appplicable_models = groups[0]
                                applicable_kw_str = groups[1]
                                keywords = clean_list(applicable_kw_str, ",", ["–"])
                                data_sheet.keywords[appplicable_models] = keywords
                            keywords_str = keywords_str.replace(full_text, "")

                            multi_search = re.search(
                                r"(.+?):(.+?)(?=[A-Z][A-Z]|!@#)", keywords_str
                            )
                        # print(keywords_str)
                    # print(data_sheet.unit_name + ": " + str(data_sheet.keywords))
            """ if "KEYWORDS:" in current_word and "FACTION KEYWORDS" not in current_word:
                name = current_word.replace("KEYWORDS:", "")
                data_sheet.unit_name = name
                current_word = ""
                keywords_open = True """

            if "FACTION KEYWORDS:" in current_word:
                faction_keywords_open = True
                current_word = ""

            if (
                data_sheet.unit_name != ""
                and data_sheet.unit_name.lower() in current_word.lower()
                and keywords_open
            ):
                parse_keywords(current_word, data_sheet, "keywords")
                current_word = ""
                keywords_open = False

            if faction_keywords_open == True and "ABILITIES" in current_word:
                parse_keywords(
                    current_word.replace("ABILITIES", ""),
                    data_sheet,
                    "faction_keywords",
                )
                current_word = ""
                faction_keywords_open = False

            if ranged_keyword in current_word:
                current_word = current_word.replace(ranged_keyword, "")
                ranged_open = True
                weapon_open = True
                current_weapon = C.Weapon()
                weapon_strs = []

            if melee_keyword in current_word:
                current_word = current_word.replace(melee_keyword, "")
                melee_open = True
                weapon_open = True
                current_weapon = C.Weapon()
                ranged_open = False
                weapon_strs = []

        core_abilities = re.search("CORE:(.+?)[A-Z]{2}", text_string)
        faction_abilities = None
        if army_rule is not None:
            faction_abilities = re.search(r"(?i)" + army_rule, text_string)

        if core_abilities is not None:
            for group in core_abilities.groups():
                parse_keywords(group, data_sheet, "core_abilities")
                current_word = current_word.replace("CORE:" + group, "")

        if faction_abilities is not None:
            group = faction_abilities.group()
            if group is not None:
                parse_keywords(group, data_sheet, "faction_abilities")
                current_word = current_word.replace("FACTION: " + group, "")

        unit_abilities = []
        search_term = re.search("(?:[A-Z][^\.!?]*[\.!?])", current_word)
        current_ability = ""
        wargear_abilities_open = False
        wargear_abilities = []
        while search_term is not None:
            ability_line = search_term.group()
            is_ability_start = re.match("^[A-Z][a-zA-Z ]+\:", ability_line) is not None

            if "WARGEAR ABILITIES" in ability_line:
                wargear_abilities_open = True
                """ print("wargear current: " + current_ability) """
                unit_abilities.append(current_ability)
                ability_line = ability_line.replace("WARGEAR ABILITIES", "")
                current_ability = ability_line
                current_word = current_word.replace("WARGEAR ABILITIES", "")

            if is_ability_start == True:
                if current_ability != "":
                    if wargear_abilities_open == True:
                        wargear_abilities.append(current_ability)
                        current_ability = ""
                    else:
                        unit_abilities.append(current_ability)
                        current_ability = ""
                current_ability = ability_line

            else:
                current_ability += " " + ability_line

            current_word = current_word.replace(ability_line, "")
            search_term = re.search("(?:[A-Z][^\.!?]*[\.!?])", current_word)

        if current_ability not in unit_abilities and wargear_abilities_open == False:
            unit_abilities.append(current_ability)
        if current_ability not in wargear_abilities and wargear_abilities_open == True:
            wargear_abilities.append(current_ability)

        if len(unit_abilities) > 0:
            data_sheet.unit_abilities = parse_abilities(unit_abilities)
        if len(wargear_abilities) > 0:
            data_sheet.wargear_abilities = parse_abilities(wargear_abilities)

        if "MTSVWLDOC" in text_string:
            search_term = re.search("MTSVWLDOC(.*)", text_string)
            if search_term is not None:
                data_sheet.profiles = find_stat_profiles(raw_text, data_sheet.unit_name)
                if len(data_sheet.profiles) > 1:
                    data_sheet.issue_flag = True

        invuln_search = re.search("INVULNERABLE SAVE(\d\+)", text_string)
        if invuln_search is not None:
            invuln_term = invuln_search.groups()
            data_sheet.invulnerable_save = invuln_term[0].strip()

    if "WARGEAR OPTIONS" in text_string:
        data_sheet = previous_datasheet

        if data_sheet is not None:
            data_sheet.wargear_options = parse_options(
                text_string, "WARGEAR OPTIONS([\s\S]*?)UNIT COMPOSITION"
            )

            data_sheet.composition = parse_options(
                text_string, "UNIT COMPOSITION(.+?[a-z])[A-Z]"
            )

            leader = parse_options(text_string, "LEADER(.+?[a-z])[A-Z]")
            if leader is not None and len(leader) > 0 and "This model " in leader[0]:
                data_sheet.leader = leader[1:]

            equipped_term = re.search(
                "UNIT COMPOSITION(.+?[a-z])([A-Z].+?[\.])[A-Z]", text_string
            )
            if equipped_term is not None and equipped_term.groups()[1] is not None:
                data_sheet.equipped_with = equipped_term.groups()[1]
    return data_sheet


env_props = "config/environment.properties"


def clean_list(str_value: str, separator: str, remove: list = []):
    cleaned_str = str_value
    for removed_str in remove:
        cleaned_str = str_value.replace(removed_str, "").strip()
    strings = cleaned_str.split(separator)
    str_values = []
    for string in strings:
        stripped = string.strip()
        if stripped != "":
            str_values.append(stripped)
    return str_values


def send_datasheet_to_db(unit_name, json_data):
    connection_settings = DB.ConnectionSettings(env_props)
    conn = pymysql.connect(
        user=connection_settings.user,
        passwd=connection_settings.password,
        host=connection_settings.host,
        db=connection_settings.dbname,
    )

    _json_data = json_data.decode("utf-8")

    statement = f"INSERT INTO data_cards (unit_name, json_data) VALUES ('{unit_name}', '{_json_data}')"
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    conn.close()


def nl():
    print("\n")


# TODO: change how abilities are stored to account for modified versions of the base rule, i.e. reanimation protocols
def build_data_sheets(file_path):
    fd = open(file_path, "rb")
    viewer = SimplePDFViewer(fd)
    previous_datasheet = None
    page = 1
    army_name = ""
    army_rule = None
    data_sheets = {}
    print("Starting PDF scan")
    for canvas in viewer:
        if page == 1:
            text = "".join(canvas.strings)
            search_term = re.search("(.+?)(?= – |DETACHMENT|ARMY RULE)", text)

            if search_term is not None:
                army_name = search_term.groups()[0].strip()
            army_rule_search = re.search("ARMY RULE.+?([A-Z][A-Z].+?)[A-Z][a-z]", text)
            if army_rule_search is not None:
                army_rule = army_rule_search.groups()[0]

        _data_sheet = build_data_sheet(canvas.strings, previous_datasheet, army_rule)

        if army_name != "" and _data_sheet.unit_name != "":
            _data_sheet.army_name = army_name
        page += 1
        output = "./output/"

        if (
            _data_sheet is not None
            and _data_sheet.unit_name != ""
            and previous_datasheet.unit_name == _data_sheet.unit_name
        ):
            data_sheets[_data_sheet.unit_name] = _data_sheet.toDict()
            """ if not os.path.exists("./output/images/" + army_name):
                os.mkdir("./output/images/" + army_name) """

            """ for image in canvas.images:
                _image = canvas.images[image]
                pil_image = _image.to_Pillow()
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")
                    pil_image = ImageChops.invert(pil_image)
                    enhancer = ImageEnhance.Brightness(pil_image)
                    pil_image = enhancer.enhance(0.8)
                    enhancer = ImageEnhance.Contrast(pil_image)
                    pil_image = enhancer.enhance(1.4)
                    enhancer = ImageEnhance.Color(pil_image)
                    pil_image = enhancer.enhance(1.3)
                    pil_image.save(
                        "output/images/"
                        + army_name
                        + "/"
                        + _data_sheet.unit_name
                        + ".png"
                    ) """

        previous_datasheet = _data_sheet
    datapath = (
        "/home/joseph/coding_base/warhammer10th/python_code/pdf_reader/src/output/"
    )
    io = open(datapath + army_name + ".json", "w")
    io.write(json.dumps(data_sheets))
    io.close()
    return {"data_sheets": data_sheets, "army_name": army_name}


def upload_from_file(file_path):
    datasheets = []
    with open(file_path, "r") as json_data:
        datasheets = json.load(json_data)

    for datasheet_str in datasheets:
        datasheet = json.loads(datasheet_str)
        json_data = bytes(json.dumps(datasheet), "utf8")
        unit_name = datasheet["unit_name"]
        if unit_name is not None and unit_name != "":
            try:
                send_datasheet_to_db(unit_name, json_data)
            except Exception as inst:
                print(inst)


def build_points(file_path):
    fd = open(file_path, "rb")
    viewer = SimplePDFViewer(fd)
    first_page = True
    points_by_army = {}
    current_army = ""
    unit_points = []
    print("Starting points scan")
    for canvas in viewer:
        if first_page == False:
            raw = canvas.strings
            raw[-1] = "EOF"
            text = "".join(raw)

            search_term = re.search(r"(.+?[A-Z])[A-Z][a-z]", text)

            army_name = ""
            if search_term is not None:
                army_name = search_term.groups()[0]
                if "ENHANCEMENTS" not in army_name:
                    current_army = army_name
                    unit_points = []
                else:
                    army_name = current_army

            text = text.replace(army_name, "")
            search_term = re.search(
                r"(.+?)\d", text
            )  # re.search(r"(.+?)((\d+ model.).+?(\d+ pts))+", text)
            current_unit = C.UnitComposition()  # (([0-9]* models).+?(\d+ pts))+
            while search_term is not None:
                groups = search_term.groups()
                unit_name = groups[0]

                if "DETACHMENT ENHANCEMENTS" not in unit_name:
                    is_member = False
                    point_search = re.search(r"(.+?s)[A-Z]", text)

                    full_match_search = re.search(r"(.+?pts)[A-Z]", text)
                    full_match = ""

                    if full_match_search is not None:
                        full_match = full_match_search.groups()[0]
                    else:
                        print("match: " + text)

                    if point_search is not None:
                        points_text = point_search.groups()[0]
                        is_member = "+" in points_text

                        if unit_name != current_unit.unit_name and not is_member:
                            if current_unit.unit_name != "":
                                unit_points.append(current_unit.toDict())
                            current_unit = C.UnitComposition()
                            current_unit.unit_name = unit_name

                        text = text.replace(full_match, "")

                        if is_member == True:
                            cleaned = points_text.replace(".", "")
                            split = cleaned.split(" ")
                            pt_index = 0

                            for val in split:
                                if "+" in val:
                                    break
                                pt_index += 1

                            option_name = " ".join(split[0:pt_index])
                            option_pts = "".join(split[pt_index:])
                            current_unit.points[option_name] = option_pts
                        else:
                            unit_points_search = re.search(
                                r"(\d.+?model.+?)\.+?(\d.+? pts)", points_text
                            )

                            while unit_points_search is not None:
                                point_groups = unit_points_search.groups()
                                current_unit.points[point_groups[0]] = point_groups[1]
                                points_text = points_text.replace(
                                    unit_points_search.group(), ""
                                )
                                if "Tidewall Defence Platform" in full_match:
                                    print(points_text)
                                unit_points_search = re.search(
                                    r"(\d.+?model.+?)\.+?([\+|\d].+? pts)", points_text
                                )
                    else:
                        print("bad match: " + text)
                        text = ""
                else:
                    text = ""

                search_term = re.search(r"(.+?)[\.|\d]", text)
            points_by_army[army_name] = unit_points
        else:
            first_page = False
    io = open(
        "/home/joseph/coding_base/warhammer10th/python_code/pdf_reader/src/output/POINTS.json",
        "w",
    )
    io.write(json.dumps(points_by_army))
    io.close()
    print("Points scan complete")
    return points_by_army
    # print("".join(viewer.canvas.strings))


def find_in_object_list(property: str, value: str, items: list):
    result = None
    for item in items:
        try:
            if hasattr(item, property):
                prop = getattr(item, property)
                if isinstance(prop, str) and prop.lower() == value.lower():
                    result = item
            if result == None:
                raise Exception
        except Exception as inst:
            try:
                prop = item[property]
                if isinstance(prop, str) and prop.lower() == value.lower():
                    result = item
            except Exception as inst:
                pass
    return result


output = "/home/joseph/coding_base/warhammer10th/warhammer10th/src/assets/data-files/"


def scan_all_pdfs():
    root = "./pdfs/"
    os.chdir(root)
    all_files = os.listdir()
    pdfs = []
    armies = {}
    for file in all_files:
        if file.endswith(".pdf"):
            pdfs.append(file)

    length = len(pdfs)
    count = 0

    for pdf in pdfs:
        if pdf == "points.pdf":
            points = build_points(pdf)
        else:
            print("Scanning: " + pdf)
            data = build_data_sheets(pdf)
            armies[data["army_name"]] = data["data_sheets"]
        count += 1
        percent = round(count / length * 100, 2)
        print(str(percent) + "% complete")

    if points is not None and len(armies) > 0:
        print("success")
        for army, point_list in points.items():
            try:
                army_data = armies[army]

                if army_data is not None:
                    for composition in point_list:
                        unit_name = composition["unit_name"]
                        if isinstance(unit_name, str):
                            unit_name = unit_name.upper()
                        data_sheet = None
                        try:
                            data_sheet = army_data[unit_name]
                        except Exception as inst:
                            pass

                        if data_sheet is not None:
                            data_sheet["composition"] = composition["points"]
                            army_data[unit_name] = data_sheet
            except Exception as inst:
                print(inst)
                print(army + " not found in PDF data")

        io = open(output + "armies.json", "w")
        io.write(json.dumps(armies))
        io.close()


army_equivalents = {"SPACE MARINES": "ADEPTUS ASTARTES"}


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


known_issue_regex = [
    r"(\".+?)IN ",  # 'CAPTAININ => CAPTAIN IN etc..
]


def validate_json(data: dict, indent=""):
    for key, value in data.items():
        if isinstance(value, dict):
            validate_json(value, indent + "  ")
        elif isinstance(value, list):
            validate_list(value, indent)
        else:
            for regex in known_issue_regex:
                if isinstance(value, str):
                    search = re.search(regex, key)
                    if search is not None:
                        print("Potential problem: " + str(value))


def validate_list(data: list, indent=""):
    for item in data:
        if isinstance(item, dict):
            validate_json(item, indent + "  ")
        else:
            pass  # print(indent + "listvalue: " + item)


def validate_armies_json():
    os.chdir("/home/joseph/coding_base/warhammer10th/python_code/pdf_reader/src/output")
    all_files = os.listdir()
    json_files = []
    for file in all_files:
        if file.endswith(".json") and file != "POINTS.json":
            json_files.append(file)

    for json_file in json_files:
        file_data = {}
        print(json_file)
        with open(json_file, "r") as json_data:
            file_data = json.load(json_data)

            if isinstance(file_data, dict):
                validate_json(file_data)
            else:
                validate_list(file_data)


def assemble_armies_json():
    os.chdir("./output/")
    all_files = os.listdir()
    json_files = []
    armies = {}

    for file in all_files:
        if file != ".json" and file.endswith(".json"):
            json_files.append(file)
    for json_file in json_files:
        with open(json_file, "r") as json_data:
            army_data = json.load(json_data)

            for unit_name, unit_data in army_data.items():
                try:
                    army_name = unit_data["army_name"]
                    if isinstance(army_name, str) and army_name != "":
                        armies[army_name] = army_data
                        print(army_name + " is loaded")
                        break
                except Exception as inst:
                    print(inst)
    points_by_army = {}
    with open(
        "/home/joseph/coding_base/warhammer10th/python_code/pdf_reader/src/output/POINTS.json",
        "r",
    ) as json_data:
        points_by_army = json.load(json_data)

    for army, point_list in points_by_army.items():
        try:
            if d_hasattr(army_equivalents, army):
                army_data = d_getattr(army_equivalents, army)
            army_data = armies[army]

            if army_data is not None:
                for composition in point_list:
                    unit_name = composition["unit_name"]
                    if isinstance(unit_name, str):
                        unit_name = unit_name.upper()
                    data_sheet = None
                    try:
                        data_sheet = army_data[unit_name]
                    except Exception as inst:
                        nl()
                        print(inst)
                        print("unit error")
                        # print("data_sheet: " + str(data_sheet))
                        # nl()
                        # print("unit_name: " + str(unit_name))
                        nl()
                        print("army_data: " + str(army_data))
                        nl()
                        nl()
                        resume = input()

                    if data_sheet is not None:
                        data_sheet["composition"] = composition["points"]
                        army_data[unit_name] = data_sheet
        except Exception as inst:
            print(inst.args)
            print(army + " not found in PDF data")

    io = open(output + "armies.json", "w")
    io.write(json.dumps(armies))
    io.close()


# validate_armies_json()
# scan_all_pdfs()
# build_points("./pdfs/points.pdf")
assemble_armies_json()
# build_data_sheets("./pdfs/adepta sororitas.pdf")
