import sys
import os

import yaml
from jinja2 import Template

raw = open(sys.argv[1]).read()
parsed = yaml.load(raw)

template_dir = os.path.join(os.path.split(sys.argv[1])[0], "conf")

try:
    deploy_root = sys.argv[2].rstrip("/")
except IndexError:
    deploy_root = "/var/praekelt"

for key, value in parsed.items():
    template = Template(
        open(os.path.join(template_dir, "%s.conf.in" % key), "r").read()
    )
    rendered = template.render(deploy_root=deploy_root, **value)
    #print rendered
    fp = open(os.path.join(template_dir, "%s.conf" % key), "w")
    fp.write(rendered)
    fp.close()
