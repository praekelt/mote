from __future__ import unicode_literals

import copy
import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_EXCEPTION
from importlib import import_module

import dill

from django.conf import settings
from django.db import connection
from django.template.base import logger, Node, NodeList
from django.test.client import RequestFactory
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


def NodeList_render(self, context):

    from mote.templatetags.mote_tags import RenderNode

    # Check that parallel is enabled
    try:
        enabled = settings.MOTE["parallel"]
    except (AttributeError, KeyError):
        enabled = False

    # First pass to see if parallel is required for this nodelist. If
    # current process is already parallelized we can't use parallel.
    has_multi = False
    if enabled and ("request" in context) \
        and not hasattr(context["request"], "__already_parallel__"):
        for node in self:
            if isinstance(node, RenderNode):
                has_multi = True
                break

    # Original code if no parallel required
    if not has_multi:
        bits = []
        for node in self:
            if isinstance(node, Node):
                bit = node.render_annotated(context)
            else:
                bit = node
            bits.append(force_text(bit))
        return mark_safe("".join(bits))

    # Build a new minimal picklable context and request
    new_context = context.new({
        "request": RequestFactory().get("/"),
    })
    new_context.request = new_context["request"]
    if "element" in context:
        new_context["element"] = context["element"].dotted_name
    if "data" in context:
        new_context["data"] = context["data"]
    if "project" in context:
        new_context["project"] = context["project"]
    if "__mote_project_id__" in context:
        new_context["__mote_project_id__"] = context["__mote_project_id__"]
    pickled_context = dill.dumps(new_context)

    with ProcessPoolExecutor() as pool:

        # List of jobs that run on other cores
        futures = []

        # Completion order is not fixed so incorporate an index
        bits = []
        for index, node in enumerate(self):
            if isinstance(node, RenderNode):
                bits.append("")
                futures.append(pool.submit(
                    render_annotated_multi,
                    dill.dumps(node),
                    pickled_context,
                    index
                ))
            elif isinstance(node, Node):
                bits.append(force_text(node.render_annotated(context)))
            else:
                bits.append(force_text(node))

        # Let the futures complete
        results = wait(futures, return_when=FIRST_EXCEPTION)

        while results[0]:
            method = results[0].pop().result
            if method is not None:
                index, rendered = method()
                bits[index] = force_text(rendered)

        return mark_safe("".join(bits))


def render_annotated_multi(node, context, index):
    # Multiprocess does a deepcopy of the process and this includes the
    # database connection. This causes issues because DB connection info is
    # recorded in thread locals. Close the DB connection - Django will
    # automatically re-establish it.
    connection.close()

    # Do the actual rendering
    node = dill.loads(node)
    context = dill.loads(context)
    setattr(context["request"], "__already_parallel__", True)
    result = node.render_annotated(context)
    return index, result


logger.info("Mote patching django.template.base.NodeList")
NodeList.render = NodeList_render
