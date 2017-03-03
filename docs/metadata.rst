Managing Metadata
#################

Each category - that is **project**, **aspect** or **pattern** - displayed in the Mote interface will, by default, have its name inferred from its directory name, and its position within the navigation bar sorted alphabetically.

Whilst this is a sane default, it is not particularly aesthetically pleasing.

Fortunately, these bits of information may be overwritten by creating a ``metadata.json`` per category folder.

Metadata Spec
~~~~~~~~~~~~~

.. code-block:: json

    {
        "title": "Category Item Title",
        "description": "This is relevant to indiviual patterns, and may currently be ignored on the project and aspect level.",
        "position": 1
    }

Mote supports the concept of layering pattern libraries. It makes it possible
for a pattern library to inherit from one or more pattern libraries.  Define
the list of parent pattern libraries in the project's metadata.json. Items
later in the list override preceding items, so if both ``praekelt`` and
``praekeltblue`` define an element ``panel`` then ``praekeltblue`` wins.:

.. code-block:: json

    {
        "patterns": ["praekelt", "praekeltblue"]
    }

