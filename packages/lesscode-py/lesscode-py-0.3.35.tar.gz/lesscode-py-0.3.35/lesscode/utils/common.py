from copy import deepcopy


def get_value_from_dict(data: dict, key: str = None):
    value = deepcopy(data)
    if key:
        key_list = key.split(".")
        for k in key_list:
            if not isinstance(value, dict):
                break
            else:
                value = value.get(k)
    return value


# 去空
def eliminate_empty(list):
    return [x for x in list if x is not None]


def dict2single_dict(source_dict: dict, parent_name: str = ""):
    result = {}
    for k, v in source_dict.items():
        column_name = f"{parent_name}.{k}" if parent_name else k
        if not v or column_name in result:
            continue
        if isinstance(v, dict):
            result.update(dict2single_dict(v, column_name))
        else:
            result[column_name] = v
    return result
