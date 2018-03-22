Mote Explorer
#############

.. contents::

The Mote Explorer is a web browsable interface of all the projects visible to
Mote. It is normally accessible at ``http://host/mote/``.

The Explorer renders each pattern in its own iframe to ensure complete
separation of CSS and JavaScript.

URL's
-----

The underlying URL's used by the Explorer are useful to view rendered patterns
in isolation because it avoids the overhead of loading the navigational
elements.

To see the rendered version of eg. ``myproject.browser.atoms.button`` visit:

.. code-block:: html

    http://host/mote/project/iframe/myproject/browser/atoms/button/

To see the rendered version of eg. ``myproject.browser.atoms.button.alert`` visit:

.. code-block:: html

    http://host/mote/project/iframe/myproject/browser/atoms/button/alert

All the URL patterns accept a ``beautify=1`` parameter if you need legible
HTML formatting:

.. code-block:: html

    http://host/mote/project/iframe/myproject/browser/atoms/button/?beautify=1

