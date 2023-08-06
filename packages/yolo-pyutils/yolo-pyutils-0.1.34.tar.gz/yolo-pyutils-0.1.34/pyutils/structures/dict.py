from pyutils.structures import string


# build rows from nested dict
# input: map<beanName: map<metricName: metricValue>>
#   e.g. {"bean1":{"m1":"v1", "m2":"v2"}, "bean2":{"m3":"v3"}}
# output: table with columns [beanName, metricName, metricValue]
#   e.g.  | bean1 | m1 | v1 |
#         | bean1 | m2 | v2 |
#         | bean2 | m3 | v3 |
def build_rows_from_nested_dict(nested_dict):
    keys = list()
    rows = list()
    __process_single_level_of_nested_dict(nested_dict, keys, rows)
    return rows


def __process_single_level_of_nested_dict(data, keys, rows):
    if isinstance(data, dict):
        for key, value in data.items():
            __process_single_level_of_nested_dict(value, keys + [key], rows)
    else:
        row = list(keys) + [data]
        rows.append(row)


# support grouping iterable data by multiple dimensions,
# return hierarchical dictionaries such as:
# group_by_l1_key1 : group_by_l2_key1 : data_dict_key1 : data_value1
#                                       data_dict_key2 : data_value2
#                    group_by_l2_key2 : data_dict_key3 : data_value3
#                                       data_dict_key4 : data_value4
# group_by_l1_key2 : group_by_l2_key1 : data_dict_key5 : data_value5
def complex_group_by_dict(iterable_data, group_by_fn_list, sub_dict_get_key_fn):
    ret_dict = dict()
    for item in iterable_data:
        group = ret_dict
        for group_by_fn in group_by_fn_list:
            group_by_key = group_by_fn(item)
            group = get_or_new_value(group, group_by_key, dict)
        item_key = sub_dict_get_key_fn(item)
        group[item_key] = item
    return ret_dict


# if the specified key can be found in the dict, return the related value,
# if not, add a new value into the dict then return it.
def get_or_new_value(data_dict, key, new_value_fn):
    data = data_dict.get(key)
    if data is None:
        if isinstance(new_value_fn, tuple):
            data = new_value_fn[0](*new_value_fn[1:])
        else:
            data = new_value_fn()
        data_dict[key] = data
    return data


def group_by_dict(iterable_data, group_by_fn, sub_dict_get_key_fn):
    ret_dict = dict()
    for item in iterable_data:
        group_by_key = group_by_fn(item)
        group = get_or_new_value(ret_dict, group_by_key, dict)
        item_key = sub_dict_get_key_fn(item)
        group[item_key] = item
    return ret_dict


def group_by_list(iterable_data, group_by_fn):
    ret_dict = dict()
    for item in iterable_data:
        group_by_key = group_by_fn(item)
        group = get_or_new_value(ret_dict, group_by_key, list)
        group.append(item)
    return ret_dict


# format configuration dict via replacing variables with the values given by the dict itself or other dict.
def format_conf_dict(conf_dict, other_conf_dict):
    for conf_key, conf_value in conf_dict.items():
        replaced_value = string.replace_var(conf_value, [conf_dict, other_conf_dict])
        conf_dict[conf_key] = replaced_value


# return error_message
def check_dict(target_dict, required_keys):
    required_missing = []
    for required_key in required_keys:
        if required_key not in target_dict:
            required_missing.append(required_key)
    if len(required_missing) > 0:
        return "{} is required but missing!".format(required_missing)
    return None
