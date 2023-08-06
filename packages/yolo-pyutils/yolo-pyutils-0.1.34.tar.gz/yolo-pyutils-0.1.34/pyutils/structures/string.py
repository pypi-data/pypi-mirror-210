import re
import json


CONF_VAR_PATTERN = re.compile('\\${[a-zA-Z0-9_.-]+}')


def replace_var(content, var_data_dicts):
    matched_vars = CONF_VAR_PATTERN.findall(content)
    for var in matched_vars:
        var_name = var[2:-1]
        for var_data_dict in var_data_dicts:
            env_value = var_data_dict.get(var_name)
            if env_value is not None:
                break
        if env_value is None:
            raise RuntimeError('env var {} defined in conf file not found!'.format(var))
        content = content.replace(var, env_value)
    return content


def parse_json_str(json_str):
    if json_str is not None:
        # avoid "INF" causing json load failure
        if json_str.find("INF,") >= 0:
            json_str = json_str.replace("INF,", "\"INF\",")
        # avoid "NaN" causing json load failure
        if json_str.find("NaN,") >= 0:
            json_str = json_str.replace("NaN,", "\"NaN\",")
        return json.loads(json_str)
    return None

