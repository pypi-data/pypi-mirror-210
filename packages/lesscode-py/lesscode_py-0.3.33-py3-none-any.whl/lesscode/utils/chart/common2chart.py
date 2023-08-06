from copy import deepcopy

from lesscode.utils.common import get_value_from_dict


def money_format(value, is_int=False):
    value = "%.2f" % float(value)
    components = str(value).split('.')
    if len(components) > 1:
        left, right = components
        right = '.' + right
    else:
        left, right = components[0], ''
    result = ''
    while left:
        result = left[-3:] + ',' + result
        left = left[:-3]
    if is_int:
        return result.strip(',')
    return result.strip(',') + right


def get_value_by_key(data: dict, key: str = None):
    if key:
        data = data.get(key)
    return data


def get_data_by_deep_from_dict(data: dict, deep: int):
    if not data:
        return {}
    result = {}
    if deep != 0:
        for _v in data.values():
            sub_result = get_data_by_deep_from_dict(deepcopy(_v), deep - 1)
            result.update(sub_result)
    else:
        return deepcopy(data)
    return result


def dict2ring(data: dict, unit: str = "", second_unit: str = "", key: str = "count", title: str = "", flag=True):
    """
    单层字典转饼图或者环形图
    :param flag: 百分比是否*100
    :param data: 需要转换的数据，实例1：{"测试1":{"count":1},"测试2":{"count":1}},实例2：{"测试1":1,"测试2":2}
    :param unit: 百分比单位
    :param second_unit: 数值单位
    :param key: 数据key
    :param title:图题
    :return:
    """
    total = 0
    for name, value in data.items():
        total += get_value_by_key(value, key)
    if flag:
        weight = 100
    else:
        weight = 1
    result = {
        "title": title,
        "data": [{"name": name,
                  "unit": unit,
                  "value": (money_format(get_value_by_key(value, key) / total * weight)) if total > 0 else 0,
                  "second_unit": second_unit,
                  "second_value": get_value_by_key(value, key)} for name, value in data.items()]
    }
    return result


def dict2columnar(data: dict, num: int, key_map: dict = None, title: str = "",
                  x_unit="", y_unit: str = "", data_key="count", default=None):
    """
    字典转柱状图，单柱或者多柱
    :param data: 字典数据
        实例1：{"河南省": 1, "北京市": 1}
        实例2：{"河南省": {"人工智能": 1, "传感器": 1}, "北京市": {"人工智能": 1, "传感器": 1}}
        实例3：{"河南省": {"人工智能": {"count":1}, "传感器": {"count":1}}, "北京市": {"人工智能": {"count":1}, "传感器": {"count":1}}}
    :param num: 柱子个数
    :param key_map: 字段映射
        实例1：{"人工智能": {"name": "人工智能", "data_key": "ren"}, "传感器": {"name": "传感器", "data_key": "chuan"}}
        实例2：{"人工智能": {"data_key": "ren"}, "传感器": {"data_key": "chuan"}}
    :param title: 图题
    :param x_unit: x轴单位
    :param y_unit: y轴单位
    :param data_key: 数据key
    :param default:获取不到内容时的默认数据
    :return:
    """
    first_keys = list(data.keys())
    result = {
        "title": title,
        "xAxis": first_keys,
        "yAxis": [],
        "xUnit": x_unit,
        "yUnit": y_unit
    }
    if num == 1:
        for first_key, first_value in data.items():
            value = get_value_by_key(first_value, data_key) if isinstance(first_value,
                                                                          dict) and data_key else first_value
            info = {"name": key_map.get(first_key, {}).get("name", first_key) if key_map else first_key,
                    "data_key": key_map.get(first_key, {}).get("data_key", first_key) if key_map else first_key,
                    "value": get_value_by_key(value, data_key) if isinstance(value, dict) and data_key else value}
            result["yAxis"].append(info)
    if num == 2:
        total_dict = {}
        names = []
        for first_key, first_value in data.items():
            unit_dict = {}

            for second_key, second_value in first_value.items():
                unit_dict[second_key] = get_value_by_key(second_value, data_key) \
                    if isinstance(second_value, dict) and data_key else second_value
                if second_key not in names:
                    names.append(second_key)
            total_dict[first_key] = unit_dict
        for name in names:
            info = {"name": key_map.get(name, {}).get("name", name) if key_map else name,
                    "data_key": key_map.get(name, {}).get("data_key", name) if key_map else name,
                    "value": []}
            for first_key in first_keys:
                info["value"].append(total_dict.get(first_key, {}).get(name, default))
            result["yAxis"].append(info)
    return result


def list2table(title: str, head, data: list, column_keys: dict = None, index_dict: dict = None):
    """
    list数据转换成表格
    :param index_dict: 索引列信息，实例：{"start":1,"column_name":"序号"，"index"："index"，"key"："index"}
    :param column_keys:数据对应点的keys，实例1：{"name1":"name2"} 说明：name1：接口返回字段名，name2:是数据的key,支持多层key，通过.连接，例如：basic.name
    :param data: es返回的数据
    :param title: 表格标题，字符串类型
    :param head: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"企业名称": "name"}]

    """

    result = {
        "title": title,
        "columns": [],
        "dataSource": [],
        "total": 0
    }
    if isinstance(head, dict):
        for key, value in head.items():
            result["columns"].append({"title": key,
                                      "dataIndex": value, "key": value})
    elif isinstance(head, list):
        result["columns"] = head
    else:
        raise Exception(f'head={head} is error')
    if column_keys:
        for item in data:
            data_item = {
            }
            for key, value in column_keys.items():
                data_item[key] = get_value_from_dict(item, value)
            result["dataSource"].append(data_item)
    else:
        result["dataSource"] = data
    result["total"] = len(result["dataSource"])

    if index_dict:
        ix = index_dict.get("start", 1)
        index_title = index_dict.get("column_name", "序号")
        data_index = index_dict.get("index", "index")
        data_key = index_dict.get("key", "index")
        index_no = index_dict.get("index_no", 0)
        result["columns"].insert(index_no, {"title": index_title,
                                            "dataIndex": data_index, "key": data_key})
        for item in result["dataSource"]:
            item[data_key] = ix
            ix += 1

    return result


def convert(value, func):
    return func(value)


def list2table_with_page(title: str, head, data: list, column_keys: dict = None, index_dict: dict = None,
                         page_num: int = 1, page_size: int = 10, total: int = 0, column_covert: dict = None):
    """
    list数据转换成表格
    :param column_covert: {"id":str}
    :param total: 数据总数
    :param page_size: 每页数量
    :param page_num: 页码
    :param index_dict: 索引列信息，实例：{"start":1,"column_name":"序号"，"index"："index"，"key"："index"}
    :param column_keys:数据对应点的keys，实例1：{"name1":"name2"} 说明：name1：接口返回字段名，name2:是数据的key,支持多层key，通过.连接，例如：basic.name
    :param data: es返回的数据
    :param title: 表格标题，字符串类型
    :param head: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"企业名称": "name"}]

    """

    result = {
        "title": title,
        "columns": [],
        "dataSource": [],
        "total": 0
    }
    if isinstance(head, dict):
        for key, value in head.items():
            result["columns"].append({"title": key,
                                      "dataIndex": value, "key": value})
    elif isinstance(head, list):
        result["columns"] = head
    else:
        raise Exception(f'head={head} is error')
    if column_keys:
        for item in data:
            data_item = {
            }
            for key, value in column_keys.items():
                new_value = get_value_from_dict(item, value)
                if column_covert:
                    if key in column_covert:
                        new_value = convert(new_value, column_covert.get(key))
                data_item[key] = new_value
            result["dataSource"].append(data_item)
    else:
        result["dataSource"] = data
    result["total"] = total

    if index_dict:
        ix = index_dict.get("start", 1) + (page_num - 1) * page_size
        index_title = index_dict.get("column_name", "序号")
        data_index = index_dict.get("index", "index")
        data_key = index_dict.get("key", "index")
        index_no = index_dict.get("index_no", 0)
        result["columns"].insert(index_no, {"title": index_title,
                                            "dataIndex": data_index, "key": data_key})
        for item in result["dataSource"]:
            item[data_key] = ix
            ix += 1

    return result
