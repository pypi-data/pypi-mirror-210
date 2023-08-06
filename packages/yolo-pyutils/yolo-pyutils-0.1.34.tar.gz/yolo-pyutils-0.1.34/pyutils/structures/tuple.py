
def add_tuple_by_indexes(tp1, tp2):
    return tuple(map(lambda x: x[0] + x[1], zip(tp1, tp2)))


def divide_tuple_by_indexes(tp1, tp2):
    return tuple(map(lambda x: round(x[0] / x[1], 3) if x[1] != 0 else 0.0, zip(tp1, tp2)))


def sub_tuple_by_indexes(tp1, tp2):
    return tuple(map(lambda x: round(x[0] - x[1], 3), zip(tp1, tp2)))


def min_tuple_by_indexes(tp1, tp2):
    return tuple(map(lambda x: min(x[0], x[1]), zip(tp1, tp2)))
