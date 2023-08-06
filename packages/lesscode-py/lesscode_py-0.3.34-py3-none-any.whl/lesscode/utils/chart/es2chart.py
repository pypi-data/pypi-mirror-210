from lesscode.utils.common import get_value_from_dict


def es_list2table(title: str, head, data, column_keys: dict = None,
                  data_key: str = "data_list", count_key="data_count", index_dict: dict = None):
    """
    es的查询结果转换成表格
    :param index_dict: 索引列信息，实例：{"start":1,"column_name":"序号"，"index"："index"，"key"："index"}
    :param count_key: 统计字段的key
    :param data_key: 数据字段的key
    :param column_keys:数据对应点的keys，实例1：{"name1":"name2"} 说明：name1：接口返回字段名，name2:是数据的key,支持多层key，通过.连接，例如：basic.name
    :param data: es返回的数据
    :param title: 表格标题，字符串类型
    :param head: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"企业名称": "name"}]

    """

    result = {
        "title": title,
        "columns": [],
        "dataSource": [],
        "total": get_value_from_dict(data, count_key)
    }
    if isinstance(head, dict):
        for key, value in head.items():
            result["columns"].append({"title": key,
                                      "dataIndex": value, "key": value})
    elif isinstance(head, list):
        result["columns"] = head
    else:
        raise Exception(f'head={head} is error')
    if data_key:
        data_list = get_value_from_dict(data, data_key)
    else:
        data_list = data
    if column_keys:
        for item in data_list:
            data_item = {
            }
            for key, value in column_keys.items():
                data_item[key] = get_value_from_dict(item, value)
            result["dataSource"].append(data_item)
    else:
        result["dataSource"] = data_list

    if index_dict:
        ix = index_dict.get("start", 1)
        index_title = index_dict.get("column_name", "序号")
        data_index = index_dict.get("index", "index")
        data_key = index_dict.get("key", "index")
        result["columns"].append({"title": index_title,
                                  "dataIndex": data_index, "key": data_key})
        for item in result["dataSource"]:
            item[data_key] = ix
            ix += 1

    return result


def es_group2tree(data, group_list, key_name="key", index=0):
    result = []
    group = group_list[index]
    if group in data.keys():
        buckets = data.get(group, {}).get("buckets", [])
        for bucket in buckets:
            info = {
                "key": bucket.get(key_name),
                "doc_count": bucket.get("doc_count"),
                "group": group,
                "children": []
            }
            if index + 1 < len(group_list):
                g = group_list[index + 1]
                if g in bucket:
                    info["children"] = es_group2tree(bucket, group_list, key_name, index + 1)
            result.append(info)
    return result


def covert2percentage(data, key="doc_count", flag=True, children_key="children", total=0):
    if isinstance(data, list):
        for x in data:
            doc_count = x.get(key, 0)
            total += doc_count
            if children_key in x:
                x[children_key] = covert2percentage(x[children_key], key, flag, children_key, doc_count)
        for y in data:
            percentage = round(y.get("doc_count", 0) / total, 2) if total else 0
            y["percentage"] = percentage * 100 if flag else percentage
    return data


def convert_key_by_map(data, mapping: dict):
    if isinstance(data, list):
        for x in data:
            convert_key_by_map(x, mapping)
    elif isinstance(data, dict):
        for k, v in mapping.items():
            if k in data:
                data[v] = data[k]
                data.pop(k)


def es_single_group2ring(title: str, data, group_type: str, data_key="aggregations",
                         unit="%", second_unit="", flag=True):
    """
    es单分组转环形图
    :param title: 图题
    :param data: es分组原始数据
    :param group_type: 分组类型
    :param data_key: 数据key
    :param unit: 百分比单位
    :param second_unit: 数值单位
    :param flag: 百分比是否*100
    :return:
    """
    group_data = get_value_from_dict(data, data_key)
    tree = es_group2tree(group_data, [group_type])
    tree_with_percentage = covert2percentage(tree, "doc_count", flag)
    result = {
        "title": title,
        "data": [{"name": x.get("key"), "unit": unit, "value": x.get("percentage"),
                  "second_unit": second_unit, "second_value": x.get("doc_count")} for x in tree_with_percentage]
    }
    return result
