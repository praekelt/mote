from copy import deepcopy


def _deepmerge(source, delta):
    """Recursive helper"""
    
    if source is None: return delta
    if delta is None: return source

    for key, value in delta.items():

        if isinstance(value, dict):
            if (key in source) and isinstance(source[key], list):
                # We expect a list but didn"t get one. Do conversion.
                _deepmerge(source, {key: [value]})
            else:
                node = source.setdefault(key, {})
                _deepmerge(node, value)

        elif (key in source) and isinstance(value, list):
            # Use the zero-th item as an archetype
            el = deepcopy(source[key][0])
            source[key] = []
            for n in value:
                source[key].append(deepcopy(el))
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    _deepmerge(source[key][n], v)
                else:
                    source[key][n] = v

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
