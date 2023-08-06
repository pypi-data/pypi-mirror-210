import importlib

reflect_cache = {}


def generate_instance(clazz, init_args_dict):
    constructor_fn = reflect_fn(clazz)
    return constructor_fn(**init_args_dict)


def reflect_fn(fn_path):
    global reflect_cache
    fn = reflect_cache.get(fn_path)
    if fn is None:
        tmp_arrays = fn_path.rsplit('.', 1)
        # directly return eval function if no module defined
        if len(tmp_arrays) == 1:
            return eval(fn_path)
        mod = importlib.import_module(tmp_arrays[0])
        fn = getattr(mod, tmp_arrays[1])
        reflect_cache[fn_path] = fn
    return fn
