import pandas
import numpy


def init():
    # show all columns
    pandas.set_option('display.max_columns', None)
    # show all rows
    pandas.set_option('display.max_rows', None)
    # keep row data in the same line
    pandas.set_option('display.width', None)
    # show all data
    pandas.set_option('max_colwidth', None)


def get_data_frame(dict_list_data, columns):
    nested_list_data = get_nested_list_data(dict_list_data, columns)
    return pandas.DataFrame(numpy.array(nested_list_data), columns=columns)


def get_nested_list_data(dict_list_data, columns):
    nested_list_data = list()
    for dict_obj in dict_list_data:
        sublist = list()
        for column in columns:
            sublist.append(dict_obj.get(column))
        nested_list_data.append(sublist)
    return nested_list_data

