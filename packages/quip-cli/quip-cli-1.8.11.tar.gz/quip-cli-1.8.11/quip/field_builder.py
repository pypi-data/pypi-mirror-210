import uuid
import copy

def prepare_fields(fields, code):
    numbers = {}
    available_fields = { 
        "Text": list(range(1, 21)),
        "Large Text": list(range(1, 5)),
        "Integer": list(range(1, 11)),
        "Boolean": list(range(1, 11)),
        "Choice": list(range(1, 16)),
        "Credential": list(range(1, 7)),
        "Script": list(range(1, 3)),
        "Array": list(range(1, 5)),
        "Float": list(range(1, 5))
    }

    field_mapping = {}
    fields_dict = []
    for field in fields: # Check the ones having field_mapping
        name = list(field.keys())[0]
        type = list(field.values())[0]
        type = get_type_name(type)
        _field_mapping = field.get("field_mapping", None)
        if _field_mapping is not None:
            _field_mapping_number = int(str(_field_mapping).split(" ")[-1])
            if _field_mapping_number in available_fields[type]:
                field_mapping[name] = f"{type} Field {_field_mapping_number}"
                available_fields[type].remove(_field_mapping_number)
            else:
                print(f"ERROR: {type} Field {_field_mapping_number} already used.")
                exit(1)

    for field in fields:  # set field_mapping for the ones that doesn't have yet.
        name = list(field.keys())[0]
        type = list(field.values())[0]
        type = get_type_name(type)
        if code:
            if field.get("restriction", "") != "Output Only":
                print_code_samples("field", name, type)
        _field_mapping = field.get("field_mapping", None)
        if _field_mapping is None:
            field_mapping[name] = f"{type} Field {available_fields[type].pop(0)}"
    if not code: 
        print(field_mapping)

    for field in fields:
        name = list(field.keys())[0]
        type = list(field.values())[0]
        type = get_type_name(type)
        if not code: 
            print(f"{name}:{type}:{field_mapping[name]}")
        
        sequence = len(fields_dict)
        if type in ["Text", "Large Text"]:
            _dict = create_text_field(name, field_mapping[name], sequence)
        elif type == "Credential":
            _dict = create_credential_field(name, field_mapping[name], sequence)
        elif type == "Script":
            _dict = create_script_field(name, field_mapping[name], sequence)
        elif type == "Boolean":
            _dict = create_boolean_field(name, field_mapping[name], sequence)
        elif type == "Choice":
            if code:
                if field.get("dynamic", False):
                    print_code_samples("dynamic_choice", name)
            _dict = create_choice_field(name, field_mapping[name], sequence, field.get("items", []))
        elif type == "Array":
            if "titles" in field:
                name_title, value_title = field["titles"].split(",")
            elif "headers" in field:
                name_title, value_title = field["headers"].split(",")
            else:
                name_title = field["name_title"]
                value_title = field["value_title"]
            name_title = name_title.strip(" ")
            value_title = value_title.strip(" ")
            _dict = create_array_field(name, field_mapping[name], sequence, name_title, value_title)
        else:
            _dict = copy.copy(FIELD_TEMPLATE)
            _dict["name"] = name
            _dict["label"] = labelize(name)
            _dict["fieldType"] = type
            _dict["sequence"] = sequence
            _dict["fieldMapping"] = field_mapping[name]
            _dict["sysId"] = new_uuid()

        _dict = process_raw_update(field, _dict, field_mapping)

        fields_dict.append(_dict)

    return fields_dict


def prepare_template_fields(conf):
    result = {}
    set_if_not_equal(result, "name", conf.get("name", None), None)
    set_if_not_equal(result, "templateType", conf.get("template_type", None), None)
    set_if_not_equal(result, "agentType", conf.get("agent_type", None), None)
    set_if_not_equal(result, "description", conf.get("description", None), None)
    set_if_not_equal(result, "extension", conf.get("extension", None), None)
    set_if_not_equal(result, "minReleaseLevel", conf.get("min_release", None), None)
    set_if_not_equal(result, "variablePrefix", conf.get("var_prefix", None), None)
    set_if_not_equal(result, "sysId", conf.get("sys_id", None), None)
    set_if_not_equal(result, "scriptTypeWindows", conf.get("script_ext_windows", None), None)
    return result


def get_type_name(type):
    type = type.title()
    if type.lower() in ["large", "largetext", "textarea", "text area"]:
        type = "Large Text"
    elif type.lower() in ["items", "select", "option", "options", "list"]:
        type = "Choice"
    elif type.lower() in ["grid"]:
        type = "Array"
    elif type.lower() in ["creds", "cred", "credentials"]:
        type = "Credential"
    elif type.lower() in ["bool", "check", "checkbox", "check box"]:
        type = "Boolean"
    return type


def create_text_field(name, _mapping, sequence):
    field_dict = copy.copy(FIELD_TEMPLATE)
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Text"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["sysId"] = new_uuid()
    return field_dict

def create_credential_field(name, _mapping, sequence):
    field_dict = dict(copy.copy(FIELD_TEMPLATE))
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Credential"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["sysId"] = new_uuid()
    return field_dict

def create_choice_field(name, _mapping, sequence, options):
    field_dict = copy.copy(FIELD_TEMPLATE)
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Choice"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["sysId"] = new_uuid()
    field_dict["choices"] = []
    for option in options:
        _choice_dict = copy.copy(CHOICE_TEMPLATE)
        if isinstance(option, str):
            _choice_dict["fieldValue"] = option
            _choice_dict["fieldValueLabel"] = labelize(option)
        elif isinstance(option, dict):
            option_name = list(option.keys())[0]
            option_label = list(option.values())[0]
            _choice_dict["fieldValue"] = option_name
            _choice_dict["fieldValueLabel"] = option_label
        _choice_dict["sysId"] = new_uuid()
        _choice_dict["sequence"] = len(field_dict["choices"])
        field_dict["choices"].append(_choice_dict)
    return field_dict

def create_script_field(name, _mapping, sequence):
    field_dict = dict(copy.copy(FIELD_TEMPLATE))
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Script"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["sysId"] = new_uuid()
    return field_dict

def create_boolean_field(name, _mapping, sequence):
    field_dict = dict(copy.copy(FIELD_TEMPLATE))
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Boolean"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["sysId"] = new_uuid()
    return field_dict

def create_array_field(name, _mapping, sequence, name_title, value_title):
    field_dict = dict(copy.copy(FIELD_TEMPLATE))
    field_dict["name"] = name
    field_dict["label"] = labelize(name)
    field_dict["fieldType"] = "Array"
    field_dict["sequence"] = sequence
    field_dict["fieldMapping"] = _mapping
    field_dict["arrayNameTitle"] = name_title
    field_dict["arrayValueTitle"] = value_title
    field_dict["sysId"] = new_uuid()
    return field_dict

def process_raw_update(field_details, dict, field_mapping):
    dict["required"] = field_details.get("required", False)
    dict["hint"] = safe_strip(field_details.get("hint", None))
    dict["formColumnSpan"] = field_details.get("span", 1)
    dict["formStartRow"] = field_details.get("start", False)
    dict["formEndRow"] = field_details.get("end", False)
    dict["textType"] = field_details.get("text_type", "Plain")
    dict["fieldValue"] = field_details.get("default", None)
    dict["fieldRestriction"] = field_details.get("restriction", "No Restriction")
    dict["choiceAllowMultiple"] = field_details.get("allow_multiple", False)
    dict["choiceAllowEmpty"] = field_details.get("allow_empty", False)
    dict["fieldLength"] = field_details.get("length", None)
    dict["intFieldMax"] = field_details.get("max", None)
    dict["intFieldMin"] = field_details.get("min", None)

    dict["choiceDynamic"] = field_details.get("dynamic", False)
    dependencies = field_details.get("dependencies", [])
    if len(dependencies) > 0:
        _deps = []
        for dependency in dependencies:
            _deps.append(field_mapping.get(dependency))
        dict["choiceFields"] = _deps

    show_if = field_details.get("show_if", None)
    if show_if is not None:
        show_if_name = list(show_if.keys())[0]
        show_if_value = list(show_if.values())[0]
        dict["showIfField"] = field_mapping.get(show_if_name, None)
        dict["showIfFieldValue"] = show_if_value
        dict["noSpaceIfHidden"] = show_if.get("no_space", True)
        dict["requireIfVisible"] = show_if.get("required", False)
        dict["preserveValueIfHidden"] = show_if.get("preserve_value", False)
    else:
        # If show_if available ignore require_if
        required_if = field_details.get("required_if", None)
        if required_if is not None:
            required_if_name = list(required_if.keys())[0]
            required_if_value = list(required_if.values())[0]
            dict["requireIfField"] = field_mapping.get(required_if_name, None)
            dict["requireIfFieldValue"] = required_if_value

    label = field_details.get("label", None)
    if label is not None:
        dict["label"] = label

    raw = field_details.get("raw", None)
    if raw is not None:
        for k,v in raw.items():
            dict[k] = v

    return dict

def dump_fields(fields_json):
    fields = []
    reverse_field_mapping = {}
    for field_json in fields_json:
        reverse_field_mapping[field_json["fieldMapping"]] = field_json["name"]

    for field_json in fields_json:
        field = {}
        if field_json["fieldMapping"].startswith("Large Text"):
            field[field_json["name"]] = "Large Text"
        else:
            field[field_json["name"]] = field_json["fieldType"]
        set_if_not_equal(field, "label", field_json["label"], labelize(field_json["name"]))
        set_if_not_equal(field, "hint", field_json["hint"], None)
        set_if_not_equal(field, "field_mapping", field_json["fieldMapping"], None)
        set_if_not_equal(field, "default", field_json["fieldValue"], None)
        set_if_not_equal(field, "required", field_json["required"], False)
        set_if_not_equal(field, "start", field_json["formStartRow"], False)
        set_if_not_equal(field, "end", field_json["formEndRow"], False)
        set_if_not_equal(field, "span", field_json["formColumnSpan"], 1)
        set_if_not_equal(field, "text_type", field_json["textType"], "Plain")
        set_if_not_equal(field, "dynamic", field_json["choiceDynamic"], False)
        set_if_not_equal(field, "restriction", field_json["fieldRestriction"], "No Restriction")
        set_if_not_equal(field, "name_title", field_json["arrayNameTitle"], None)
        set_if_not_equal(field, "value_title", field_json["arrayValueTitle"], None)
        set_if_not_equal(field, "allow_multiple", field_json["choiceAllowMultiple"], False)
        set_if_not_equal(field, "allow_empty", field_json["choiceAllowEmpty"], False)
        set_if_not_equal(field, "length", field_json["fieldLength"], None)
        set_if_not_equal(field, "max", field_json["intFieldMax"], None)
        set_if_not_equal(field, "min", field_json["intFieldMin"], None)
        
        if field_json["fieldType"] == "Choice":
            field["items"] = []
            for choice in field_json["choices"]:
                if choice.get('fieldValueLabel') != labelize(choice.get('fieldValue')) and choice.get("useFieldValueForLabel") == False:
                    field["items"].append({f"{choice.get('fieldValue')}": f"{choice.get('fieldValueLabel')}"})
                else:
                    field["items"].append(choice.get('fieldValue'))

            if len(field_json["choiceFields"]) > 0:
                field["dependencies"] = []
                for choice_field in field_json["choiceFields"]:
                    if choice_field is None:
                        continue
                    field["dependencies"].append(reverse_field_mapping[choice_field])

        if field_json["showIfField"] is not None:
            field["show_if"] = {}
            show_if = field["show_if"]
            show_if[reverse_field_mapping[field_json["showIfField"]]] = field_json["showIfFieldValue"]
            set_if_not_equal(show_if, "no_space", field_json["noSpaceIfHidden"], True)
            set_if_not_equal(show_if, "required", field_json["requireIfVisible"], False)
            set_if_not_equal(show_if, "preserve_value", field_json["preserveValueIfHidden"], False)
        
        if field_json["requireIfField"] is not None:
            field["require_if"] = {}
            require_if = field["require_if"]
            require_if[reverse_field_mapping[field_json["requireIfField"]]] = field_json["requireIfFieldValue"]
        
        raw_items = {}
        set_if_not_equal(raw_items, "booleanNoValue", field_json["booleanNoValue"], None)
        set_if_not_equal(raw_items, "booleanValueType", field_json["booleanValueType"], "true/false")
        set_if_not_equal(raw_items, "booleanYesValue", field_json["booleanYesValue"], None)
        set_if_not_equal(raw_items, "choiceSortOption", field_json["choiceSortOption"], "Sequence")
        set_if_not_equal(raw_items, "defaultListView", field_json["defaultListView"], False)
        set_if_not_equal(raw_items, "preserveOutputOnRerun", field_json["preserveOutputOnRerun"], False)
        if len(raw_items) > 0:
            field["raw"] = raw_items
        fields.append(field)
    
    return fields


def dump_template_fields(_json):
    result = {}
    set_if_not_equal(result, "name", _json["name"], None)
    set_if_not_equal(result, "template_type", _json["templateType"], None)
    set_if_not_equal(result, "agent_type", _json["agentType"], None)
    set_if_not_equal(result, "extension", _json["extension"], None)
    set_if_not_equal(result, "min_release", _json["minReleaseLevel"], None)
    set_if_not_equal(result, "var_prefix", _json["variablePrefix"], None)
    set_if_not_equal(result, "sys_id", _json["sysId"], None)
    set_if_not_equal(result, "script_ext_windows", _json["scriptTypeWindows"], None)
    result["description"] = "" if _json["description"] is None else _json["description"]  # always show description
    return result

def dump_events(events_json):
    events = []
    if events_json is None:
        return events

    for event in events_json:
        result = {}
        set_if_not_equal(result, "name", event["name"], None)
        set_if_not_equal(result, "label", event["label"], None)
        set_if_not_equal(result, "sys_id", event["sysId"], None)
        set_if_not_equal(result, "description", event["description"], None)
        set_if_not_equal(result, "policy", event["attributesPolicy"], None)
        set_if_not_equal(result, "ttl", event["ttl"], 60)
        result["attributes"] = []
        print(event["attributes"])
        for _attr in event["attributes"]:
            attr_result = { _attr["name"]: _attr["type"] }
            set_if_not_equal(result, "label", _attr["label"], labelize(_attr["name"]))
            result["attributes"].append(attr_result)
        events.append(result)

    return events

def prepare_event_fields(events):
    result = []
    for event in events:
        _dict = {}
        _dict["name"] = event.get("name")
        _dict["label"] = event.get("label", None)
        _dict["sysId"] = event.get("sys_id", new_uuid())
        _dict["ttl"] = event.get("ttl", 60)
        _dict["description"] = event.get("description", None)
        _dict["attributesPolicy"] = event.get("attributesPolicy", "Include Attributes")
        _dict["attributes"] = []
        for _attr in event["attributes"]:
            name = list(_attr.keys())[0]
            type = list(_attr.values())[0]
            label = _attr.get("label", labelize(name))
            _dict["attributes"].append({"name": name, "label": label, "type": type})
        result.append(_dict)

    return result


def new_uuid():
    return str(uuid.uuid4()).replace("-","")


def labelize(name):
        name = name.replace("_", " ")
        name = name.replace("-", " ")
        return name.title()

def set_if_not_equal(_var, _field, value, default):
    if value != default:
        _var[_field] = value

def safe_strip(value):
    if value is None:
        return value 
    
    try:
        return value.strip()
    except:
        return value

def print_code_samples(code_type, name, type=None):
    if code_type == "field":
        if type == "Credential":
            line = ('self.{name} = {{ "user": fields.get("{name}.user", None), "password": fields.get("{name}.password", None) }}'.format(name=name))
        elif type == "Choice":
            line = ("""self.{name} = fields.get("{name}", [None])[0]""".format(name=name))
        elif type == "Boolean":
            line = ("""self.{name} = fields.get("{name}", False)""".format(name=name))
        else:
            line = ("""self.{name} = fields.get("{name}", None)""".format(name=name))
        print(line)
    if code_type == "dynamic_choice":
        print(f"@dynamic_choice_command(\"{name}\")")
        print(f"def get_{name}(self, fields):")
        print("    _fields = []")
        print("""    return ExtensionResult(
    rc = 0,
    message = "Available Fields: '{}'".format(_fields),
    values = _fields
    )""")

FIELD_TEMPLATE = {
            "arrayNameTitle" : None,
            "arrayValueTitle" : None,
            "booleanNoValue" : None,
            "booleanValueType" : "true/false",
            "booleanYesValue" : None,
            "choiceAllowEmpty" : False,
            "choiceAllowMultiple" : False,
            "choiceDynamic" : False,
            "choiceFields" : [ ],
            "choiceSortOption" : "Sequence",
            "choices" : [ ],
            "defaultListView" : False,
            "fieldLength" : None,
            "fieldMapping" : "",
            "fieldRestriction" : "No Restriction",
            "fieldType" : "",
            "fieldValue" : None,
            "formColumnSpan" : 1,
            "formEndRow" : False,
            "formStartRow" : False,
            "hint" : "",
            "intFieldMax" : None,
            "intFieldMin" : None,
            "label" : "",
            "name" : "",
            "noSpaceIfHidden" : False,
            "preserveOutputOnRerun" : False,
            "preserveValueIfHidden" : False,
            "requireIfField" : None,
            "requireIfFieldValue" : None,
            "requireIfVisible" : False,
            "required" : False,
            "sequence" : 0,
            "showIfField" : None,
            "showIfFieldValue" : None,
            "sysId" : None,
            "textType" : "Plain"
        }

CHOICE_TEMPLATE = {
                    "fieldValue" : "",
                    "fieldValueLabel" : "",
                    "sequence" : 0,
                    "sysId" : "",
                    "useFieldValueForLabel" : False
                }
