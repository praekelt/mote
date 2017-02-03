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

    return _deepmerge(deepcopy(source), delta)


# From http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
def deephash(o):
    if isinstance(o, (set, tuple, list)):
	    return tuple([deephash(e) for e in o])

    elif not isinstance(o, dict):
        return hash(o)

    new_o = deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = deephash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))
