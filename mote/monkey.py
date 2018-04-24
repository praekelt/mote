import sys

from django.conf import settings


# Monkey if parallel is enabled
try:
    enabled = settings.MOTE["parallel"]
except (AttributeError, KeyError):
    pass
else:
    vi = sys.version_info
    if vi[0] >= 3 and vi[1] >= 5:
        import mote.monkey35
    elif vi[0] == 2 and vi[1] >= 7:
        import mote.monkey27
