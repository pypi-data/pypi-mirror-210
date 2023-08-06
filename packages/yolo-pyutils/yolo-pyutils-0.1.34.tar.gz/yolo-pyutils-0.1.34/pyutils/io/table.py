from prettytable import PrettyTable
from textwrap import fill

TABLE_STYLE_COLUMN_MAX_WIDTH = 80


def generate_table(columns, rows):
    """
    :param columns: list of column names
    :param rows: list of rows
    :return: table
    """
    table = PrettyTable(field_names=tuple(columns), align='l')
    table.add_rows(rows)
    return table


def format_rows(rows, column_max_width=TABLE_STYLE_COLUMN_MAX_WIDTH):
    for row in rows:
        for index, row_item in enumerate(row):
            if isinstance(row_item, str) and len(row_item) > column_max_width:
                row[index] = fill(row_item, width=column_max_width)


def generate_grouped_info_table(grouped_keys, info_dict, format_fn_dict):
    """
    :param grouped_keys: list of grouped keys
    :param info_dict: info dict
    :param format_fn_dict: dict of format functions
    :return: table
    """
    rows = list()
    for grouped_key in grouped_keys:
        group_name = grouped_key.get('group_name')
        fields = grouped_key.get('fields')
        for no, field in enumerate(fields):
            key = field.get('key')
            value = info_dict.get(key)
            if value is None:
                continue
            format_fn = format_fn_dict.get(key) if format_fn_dict is not None else None
            if format_fn is not None:
                value = format_fn(value)
            alias = field.get('alias')
            row_data = [group_name if no == 0 else '', alias if alias is not None else key, value]
            rows.append(row_data)
    columns = ['Group', 'Field', 'Value']
    return generate_table(columns, rows)


def generate_compare_table(columns, row_keys, comparable_dicts, format_fn_dict):
    """
    :param columns: list of column names
    :param keys: list of keys
    :param comparable_dicts: list of comparable data dicts
    :param format_fn_dict: dict of format functions
    :return: table
    """
    rows = list()
    for row_key in row_keys:
        row = [row_key]
        format_fn = format_fn_dict.get(row_key) if format_fn_dict is not None else None
        for comparable_dict in comparable_dicts:
            value = comparable_dict.get(row_key)
            if value is None:
                row.append('')
            if format_fn is not None:
                value = format_fn(value)
            if isinstance(value, str) and len(value) > TABLE_STYLE_COLUMN_MAX_WIDTH:
                row.append(fill(value, width=TABLE_STYLE_COLUMN_MAX_WIDTH))
            else:
                row.append(value)
        rows.append(row)
    return generate_table(columns, rows)
