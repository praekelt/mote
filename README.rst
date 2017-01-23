Mote - the pattern library framework
====================================

.. figure:: https://travis-ci.org/praekelt/mote.svg?branch=develop
   :align: center
   :alt: Travis

Quick start
===========

Mote is intended to be a standalone library, not a project, but it can indeed be run with::

    - virtualenv ve
    - ./ve/bin/pip install -r mote/tests/requirements/19.txt
    - ./ve/bin/python manage.py migrate --run-syncdb --settings=mote.tests.settings.19
    - ./ve/bin/python manage.py runserver 0.0.0.0:8000 --settings=mote.tests.settings.19

Running Mote by reusing the test settings and requirements means the test pattern libraries
located at `mote/tests/mote/projects/` are loaded.

Browse to `http://localhost:8000/mote/` to view the pattern libraries.

Documentation
=============

Documentation is at http://mote-pattern-library-framework.readthedocs.io/en/latest/

