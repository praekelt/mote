Handling multiple projects
##########################

Let's assume that as part of your project you need to work on two different pattern libraries and have a directory structure that looks somewhat like this:

::

    .
    └── mote
        └── projects
            └── project-foo
            └── project-bar

One can assume that each of these would have a different set of statics, and thus require slightly different base templates.

Under ``project-foo`` create the following: ``mote/element/iframe.html``

Your directory tree should now look something like this:

::

    project-foo
    ├── mote
    │   └── element
    │       └── iframe.html
    └── website

This ``mote`` directory is reserved for overriding Mote's templates on a per-project basis. ``iframe.html`` is the template used within the iframe, and which encapsulates every pattern. Think of it as a Mote-specific ``base.html`` as one would find in any other Django project.

Iframe.html contents
--------------------

The contents of this file depend entirely on what your needs are for a project. A good baseline is something like the following:

.. code-block:: html

    {% load mote_tags %}
    {% load static %}

    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block extra_title %}Mobius{% endblock extra_title %}</title>

        {% block extra_meta %}
        <meta name="description" content="My Project Name" />
        {% endblock extra_meta %}

        <link rel="stylesheet" href="{% static "styles.css" %}" />
    </head>

    <body>
        {% render_element element %}

        <script type="text/javascript" src="{% static "scripts.js" %}"></script>
    </body>
    </html>
