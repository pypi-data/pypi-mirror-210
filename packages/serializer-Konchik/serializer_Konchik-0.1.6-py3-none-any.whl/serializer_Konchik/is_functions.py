def is_iterable(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__next__') and callable(obj.__iter__)
