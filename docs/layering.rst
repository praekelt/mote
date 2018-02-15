Layering
########

Mote makes it possible to base a pattern library on one or more existing pattern
libraries. For example, ``mote-lib-base`` already implements most of the common
browser patterns like buttons, images and select boxes. Re-implementing these
every time would be wasteful so it makes sense to inherit from it.

Define the list of parent pattern libraries in the project's metadata.yaml,
keeping in mind that pattern libraries later in the list override preceding
pattern libraries.

.. code-block:: yaml

    parents:
        - base
        - praekelt

Suppose we have ``mote/projects/base/library/browser/atoms/anchor`` only in the
``base`` library and our project is called ``project``. All the following
are valid names in a template in our project because Mote traverses upwards through
the inheritance hierarchy until it finds a match::

    base.browser.atoms.anchor
    praekelt.browser.atoms.anchor
    project.browser.atoms.anchor
    self.browser.atoms.anchor

Note that using ``self`` is nearly always the correct way to reference a pattern.
If an explicit version of a pattern is required then only refer to it by its actual
name.

If we are not entirely happy with the base anchor pattern we can override it
in our project by creating the directory
``mote/projects/project/library/browser/atoms/anchor``. You may recall that a
pattern contains ``element.html`` and optional files ``data.yaml``, ``usage.html``
and more. The layering mechanism enables us to override only selected files.
For example, if ``data.yaml`` from the ``base`` library is not to our liking then create
``mote/projects/project/library/browser/atoms/anchor/data.yaml`` and this data
file will be deep merged with the data file from ``base``. All the other files
are automatically inherited from the ``base`` pattern library.

The layering also makes it possible to effectively version pattern libraries since
a version is really just a pattern library based on another pattern library.
