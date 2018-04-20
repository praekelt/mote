from __future__ import unicode_literals

import copy
import logging
import multiprocessing
import time
from importlib import import_module

from django.conf import settings
from django.db import connection
from django.template.base import logger, Node, NodeList
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

import multiprocessing as mp
import traceback


class Process(mp.Process):
    """Wrap Process so exception handling propagates to parent process"""

    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
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
    if enabled and not multiprocessing.process.current_process().daemon:
        for node in self:
            if isinstance(node, RenderNode):
                has_multi = True
                break

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

    # List of jobs that run on other cores
    jobs = []

    # The process queue
    queue = multiprocessing.Queue()

    # Queue that keeps track of how many cores are in use
    cores = multiprocessing.Queue(CPU_COUNT)

    # Synchronous queue
    squeue = []

    # Everything must go into a queue. Queue completion order is not fixed so
    # incorporate the index.
    #import pdb;pdb.set_trace()
    expected_queue_size = 0
    new_context = copy.deepcopy(context)
    # _current_app is compared to a module level object variable in
    # template/context.py. Upon copy it must thus be restored to be
    # the same as the original current_app else the comparison
    # fails.
    #new_context._current_app = context._current_app
    for index, node in enumerate(self):
        if isinstance(node, Node):
            if isinstance(node, RenderNode):
                p = Process(
                    target=self.render_annotated_multi,
                    args=(node, new_context, index, queue, cores)
                )
                jobs.append(p)
                expected_queue_size += 1
            else:
                squeue.append((index, node))
        else:
            squeue.append((index, node))

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

    # Empty the queue
    pipeline = {}
    while queue.qsize():
        index, rendered, callback, data = queue.get()
        pipeline[index] = (rendered, callback, data)
    for index, node in squeue:
        pipeline[index] = node

    # Assemble bits in non-threaded order
    indexes = sorted(pipeline.keys())
    bits = []
    for index in indexes:
        item = pipeline[index]
        if isinstance(item, Node):
            rendered = item.render_annotated(context)
        elif isinstance(item, tuple):
            rendered, callback, data = item
        else:
            rendered = item
        bits.append(force_text(rendered))

    return mark_safe("".join(bits))


def NodeList_render_annotated_multi(self, node, context, index, queue, cores):
    result = ""
    try:
        # Multiprocess does a deepcopy of the process and this includes the
        # database connection. This causes issues because DB connection info is
        # recorded in thread locals. Close the DB connection - Django will
        # automatically re-establish it.
        connection.close()

        # Do the actual rendering
        result = node.render_annotated(context)

    finally:
        # Always put something on the queue
        data = {}
        callback_dotted_name = None
        queue.put((index, result, callback_dotted_name, data))

        # Signal a core is now available
        cores.get()


logger.info("template_multiprocessing patching django.template.base.NodeList")
NodeList.render = NodeList_render
NodeList.render_annotated_multi = NodeList_render_annotated_multi
