from __future__ import unicode_literals

import copy
import logging
import multiprocessing
import time
import uuid
from importlib import import_module

import dill

from django.conf import settings
from django.db import connection
from django.template.base import logger, Node, NodeList
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from concurrent.futures import ProcessPoolExecutor, wait, FIRST_EXCEPTION


CPU_COUNT = multiprocessing.cpu_count()


def NodeList_render(self, context):

    from mote.templatetags.mote_tags import RenderNode
    # Check that multiprocessing is enabled
    #try:
    #    enabled = settings.TEMPLATE_MULTIPROCESSING["enabled"]
    #except (AttributeError, KeyError):
    #    enabled = False
    enabled = True

    # First pass to see if multiprocessing is required for this nodelist. If
    # current process is already a daemon we can't use multiprocessing.
    has_multi = False
    #import pdb;pdb.set_trace()
    #print("USER?", context.get("user"))
    #if enabled and not multiprocessing.process.current_process().daemon:
    if enabled and ("__already_multiprocess__" not in context):
        for node in self:
            if isinstance(node, RenderNode):
                has_multi = True
                break

    #has_multi=  False
    try:
        pickled_context = dill.dumps(context)
    except:
        has_multi = False
    else:
        #print("PICKLING SUCCESS")
        pass

    # Original code if no multiprocessing required
    if not has_multi:
        bits = []
        for node in self:
            if isinstance(node, Node):
                bit = node.render_annotated(context)
            else:
                bit = node
            bits.append(force_text(bit))
        return mark_safe("".join(bits))

    #print("DOING MULTI", context.get("__already_multiprocess__", False))
    with ProcessPoolExecutor() as pool:

        # List of jobs that run on other cores
        futures = []

        # Completion order is not fixed so incorporate an index
        bits = []
        for index, node in enumerate(self):
            if isinstance(node, RenderNode):
                bits.append("")
                #import pdb;pdb.set_trace()
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

        #print(results)
        while results[0]:
            #import pdb;pdb.set_trace()
            method = results[0].pop().result
            #print("GOT METHOD", method)
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
    #print("CONTEXT UNPICKLED USER", context.get("user"))
    context["__already_multiprocess__"] = True
    print("IN MULTI")
    try:
        result = node.render_annotated(context)
    except:
        #print("GOT EXCEPT", node)
        raise
    #print("RESULT", result)
    return index, result


logger.info("template_multiprocessing patching django.template.base.NodeList")
NodeList.render = NodeList_render
