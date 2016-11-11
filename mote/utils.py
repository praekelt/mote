from copy import deepcopy


def _deepmerge(source, delta):
    """Recursive helper"""

    for key, value in delta.items():
        if isinstance(value, dict):
            node = source.setdefault(key, {})
            _deepmerge(node, value)
        else:
            source[key] = value

    return source


def deepmerge(source, delta):
    """Return a deep merge of two dictionaries"""

    return _merge(deepcopy(source), delta)
