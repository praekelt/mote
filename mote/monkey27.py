from __future__ import unicode_literals

import copy
import logging
import multiprocessing
import traceback
import time
from importlib import import_module

from django.conf import settings
from django.db import connection
from django.template.base import logger, Node, NodeList
from django.test.client import RequestFactory
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


CPU_COUNT = multiprocessing.cpu_count()


class Process(multiprocessing.Process):
    """Wrap Process so exception handling propagates to parent process"""

    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            raise

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception



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
    count = 0
    if enabled and not multiprocessing.process.current_process()._daemonic:
        for node in self:
            if isinstance(node, RenderNode):
                count += 1
    has_multi = count >= 2

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

    # List of jobs that run on other cores
    jobs = []

    # The process queue
    queue = multiprocessing.Queue()

    # Queue that keeps track of how many cores are in use
    cores = multiprocessing.Queue(CPU_COUNT)

    # Build a new minimal picklable context and request
    new_context = context.new({
        "request": RequestFactory().get("/"),
    })
    new_context.request = new_context["request"]
    if "element" in context:
        new_context["element"] = context["element"]
    if "data" in context:
        new_context["data"] = context["data"]
    if "project" in context:
        new_context["project"] = context["project"]
    if "__mote_project_id__" in context:
        new_context["__mote_project_id__"] = context["__mote_project_id__"]

    # Completion order is not fixed so incorporate an index
    bits = []
    expected_queue_size = 0
    for index, node in enumerate(self):
        if isinstance(node, RenderNode):
            bits.append("")
            p = Process(
                target=self.render_annotated_multi,
                args=(node, new_context, index, queue, cores)
            )
            jobs.append(p)
            expected_queue_size += 1
        elif isinstance(node, Node):
            bits.append(force_text(node.render_annotated(context)))
        else:
            bits.append(force_text(node))

    # Ensure we never run more than CPU_COUNT jobs on other cores.
    # Unfortunately multiprocessing.Pool doesn't work when used in classes so
    # roll our own.
    job_index = 0
    while queue.qsize() < expected_queue_size:
        # Use the cores queue to determine how many are free
        num_to_start = CPU_COUNT - cores.qsize()
        for i in range(num_to_start):
            if job_index < len(jobs):
                p = jobs[job_index]
                job_index += 1
                cores.put(1)
                p.daemon = True
                p.start()

        time.sleep(0.05)

    # Let the jobs complete
    for p in jobs:
        p.join()
        if p.exception:
            error, traceback = p.exception
            raise error

    # Empty the queue and update bits
    pipeline = {}
    while queue.qsize():
        index, rendered = queue.get()
        bits[index] = rendered

    return mark_safe("".join(bits))


def NodeList_render_annotated_multi(self, node, context, index, queue, cores):
    result = ""
    try:
        # Do the actual rendering
        setattr(context["request"], "__already_parallel__", True)
        result = node.render_annotated(context)

    finally:
        # Always put something on the queue
        queue.put((index, result))

        # Signal a core is now available
        cores.get()


logger.info("Mote patching django.template.base.NodeList")
NodeList.render = NodeList_render
NodeList.render_annotated_multi = NodeList_render_annotated_multi
