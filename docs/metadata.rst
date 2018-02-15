Metadata
########

.. contents::

Each item (project, aspect, pattern or variation) displayed in the Mote
Explorer has its name inferred from its directory name, and its position within
the navigation bar sorted alphabetically. Whilst this is a sane default, it is
not particularly aesthetically pleasing.

Metadata files make it possible to override these inferred values, as well as
allow the declaration of values that can never be inferrred from a directory
structure.

Common specification
--------------------

All items' metadata share the same minimal specification:

.. code-block:: yaml

    title: Item title
    description: Item description
    position: 1

Project specification
---------------------

Mote supports the concept of layering pattern libraries. It makes it possible
for a pattern library to inherit from one or more pattern libraries.  Define
the list of parent pattern libraries in the project's metadata.yaml, Pattern libraries
later in the list override preceding pattern libraries, so if both ``praekelt`` and
``praekeltblue`` define a pattern ``anchor`` then ``praekeltblue`` wins.:

.. code-block:: yaml

    parents:
        - praekelt
        - praekeltblue

