from copy import deepcopy
from collections import OrderedDict

from django.conf import settings


def _deepmerge(source, delta):
    """Recursive helper"""

    # "source" is the normative structure. Keep it.
    if source is None or delta is None:
        return source

    # If delta is an OrderedDict and the key space of delta spans the key space
    # of source then the key order of source must change to that of delta. Note
    # key id, if present, must always be first.
    if source and (source is not delta) and isinstance(delta, OrderedDict) \
        and not len(set(source.keys()) - set(delta.keys())):

        popped = {}
        for i in range(len(source)):
            k, v = source.popitem(False)
            popped[k] = v

        keys = list(delta.keys())
        if "id" in keys:
            keys.insert(0, keys.pop(keys.index("id")))
        for k in keys:
            source[k] = popped.get(k, delta[k])

    for key, value in delta.items():

        if isinstance(value, (dict)):
            if (key in source) and isinstance(source[key], list):
                # We expect a list but didn't get one. Do conversion.
                di = OrderedDict()
                di[key] = [value]
                _deepmerge(source, di)
            else:
                node = source.setdefault(key, OrderedDict())
                _deepmerge(node, value)

        elif (key in source) and isinstance(value, list):

            # By default we use the zero-th item as an archetype, unless
            # archetype is set to False in the first item in value.
            archetype = None
            if value and isinstance(value[0], dict) \
                and not value[0].get("archetype", True):
                pass
            elif source[key]:
                archetype = source[key][0]

            # Ensure source[key] can accommodate all items in value
            source[key] = []
            for n in value:
                # Remove `None` entries from lists.
                if n is not None:
                    if archetype:
                        source[key].append(deepcopy(archetype))
                    else:
                        source[key].append({})

            # Perform the deep merges
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    _deepmerge(source[key][n], v)
                elif v is not None:
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


def get_object_by_dotted_name(name, project_id=None):
    """Return object identified by eg. a.b.c.d. If "a" is "self" then use
    project_id."""

    # Avoid circular import
    from mote.models import Project, Aspect, Pattern, Element, Variation

    li = name.split(".")
    length = len(li)
    if li[0] == "self":
        if project_id is None:
            try:
                value = settings.MOTE["project"]
            except (AttributeError, KeyError):
                raise RuntimeError(
                    """Pass a valid project_id or define MOTE["project"]"""
                    + " setting for project lookup"
               )
        project = Project(project_id)
    else:
        project = Project(li[0])
    if length == 1:
        return project
    aspect = Aspect(li[1], project)
    if length == 2:
        return aspect
    pattern = Pattern(li[2], aspect)
    if length == 3:
        return pattern
    element = Element(li[3], pattern)
    if length == 4:
        return element
    variation = Variation(li[4], element)
    if length == 5:
        return variation
    return None
