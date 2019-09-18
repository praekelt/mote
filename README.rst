Mote - the pattern library framework
====================================

.. figure:: https://travis-ci.org/praekeltfoundation/mote.svg?branch=develop
   :align: center
   :alt: Travis

Quick start
===========

Run Mote using ``mote.lib.base`` as the only pattern library::

    - virtualenv ve
    - ./ve/bin/pip install -r example/requirements.txt
    - ./ve/bin/python manage.py migrate --run-syncdb --settings=example.settings
    - ./ve/bin/python manage.py runserver 0.0.0.0:8000 --settings=example.settings

Browse to `http://localhost:8000/mote/` to view the pattern libraries.

Building the docs
=================

virtualenv ve
source ve/bin/activate
pip sphinx install sphinx_rtd_theme
cd docs
make html

Documentation
=============

Documentation is at http://mote-pattern-library-framework.readthedocs.io/en/latest/

