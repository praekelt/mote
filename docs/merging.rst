Deep merging
############

.. contents::

Deep merging is the algorithm used to merge user supplied data into a
pattern's source data. This algorithm enables us to only supply small
parts of data to a pattern and have it render, instead of having to
redeclare entire data structures.

Examples
--------

We use JSON syntax since it more closely resembles Python data structures than YAML.

The simplest example completely replaces the source data:

.. code-block:: python

    source = {"foo": "bar"}
    delta = {"foo": "moo"}
    deepmerge(source, data)

    ...

    {"foo": "moo"}

Adding one more key:

.. code-block:: python

    source = {"foo": "bar"}
    delta = {"abc": "def"}
    deepmerge(source, data)

    ...

    {"foo": "bar", "abc": "def"}

Change key and add a key:

.. code-block:: python

    source = {"foo": "bar"}
    delta = {"foo": "moo", "abc": "def"}
    deepmerge(source, data)

    ...

    {"foo": "moo", "abc": "def"}

