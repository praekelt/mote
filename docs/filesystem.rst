####
Filesystem
####

Mote functions by trawling the file system to find pattern libraries and the patterns within. As such, Mote relies upon a specific convention
for how these things are structured.

At a high level, a typical Mote filesystem would look something like this:

.. literalinclude:: ./filesystem.txt
    :language: sh

Each part of this directory structure is described below.

====
Mote Root Dir
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 1

Mote begins trawling at the root of your project from the ``mote`` directory.

This directory is required, and the name may not be changed.

====
Projects
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 2

The ``projects`` directory is where you would keep, as the name suggests, all of your Mote projects.

What a project *is* is up to you. For example, you could treat **Version 1** and **Version 2** of your pattern library as separate projects,
or you could have a separate project for **ACME Website** and **ACME Emails** if you so desired.

Typically, you will find you won't need more than one project, but Mote provides you the flexibility to expand.

This directory is required, and the name may not be changed. However, the child project directories may be named arbitrarily.

====
Project
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 3,14-17

Each project's directory may be named arbitrarily, and you may have multiple project directories if necessary.

This directory can store any other files or directories relevant to the project, such as `design tokens`_, fonts and iconography.

Metadata
====

Each project may be given a bit of configuration via a ``metadata.json`` file.

This allows you to override the name which Mote infers from the filesystem with something a bit more human readable, and also allows you to specify its order within the Explorer interface.

.. code-block:: json

    {
        "title": "Look ma, no hands!",
        "position": 3
    }

Overriding the pattern base template
====

If you look at the file tree above again, you'll notice that the ``project`` directory has a child directory ``mote/element/iframe.html``.

This template functions much the same as ``base.html`` would function in Django, and each pattern will extend this template.

All Mote patterns exists in their own view, and this iframe template allows you to override the wrapping HTML.
This allows one to specify a different set of statics per project, and keeps the pattern library pure.

====
Library
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 4

This directory is required, and its name may not be changed.

It is reserved for the pattern library portion of your design system.

Sibling directories may be arbitrary and is up to you. For example, for storing
iconography in ``/symbols/``, font files in ``/fonts/`` or `design tokens`_ in ``/tokens/``.

====
Aspect
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 5-6

Think of an **aspect** as a specific implementation or use-case of a pattern library. For example, ``website`` and ``dashboard`` if you needed
different patterns for your public-facing site and your post-login environment.

Typically you will only need one, but once again Mote provides a bit of extra flexibility to you if you need it.

The directory name of an aspect is arbitrary and only one is required to exist for Mote to function.

This directory is also the highest level at which you may store source files for statics, such as CSS and JS.

====
Patterns
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 7

====
Category
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 8-9

====
Pattern
====

.. literalinclude:: ./filesystem.txt
    :language: sh
    :emphasize-lines: 10-13
