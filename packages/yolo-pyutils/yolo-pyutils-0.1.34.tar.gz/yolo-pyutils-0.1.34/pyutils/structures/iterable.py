from collections.abc import Iterable


def has_negative(its):
    return iterable_any_matches(its, lambda x: x < 0)


def iterable_any_matches(its, any_match_fn):
    if its is None:
        return False
    if isinstance(its, Iterable):
        for item in its:
            if any_match_fn(item):
                return True
    else:
        return any_match_fn(its)
    return False
