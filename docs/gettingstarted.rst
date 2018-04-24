Getting Started
################

.. contents::

Installation
------------

Mote is built using the Django web framework, which means installation is fairly simple
over a wide range of operating systems.

Standalone
**********

Run Mote using ``mote-lib-base`` as the only pattern library:

::
    - virtualenv ve
    - ./ve/bin/pip install -r example/requirements.txt
    - ./ve/bin/python manage.py migrate --run-syncdb --settings=example.settings
    - ./ve/bin/python manage.py runserver 0.0.0.0:8000 --settings=example.settings

Browse to `http://localhost:8000/mote/` to view the pattern libraries.

As part of a Django project
***************************

If you are using Django you may want to include Mote as part of your project.

#. Install or add ``mote-prk`` and ``mote-lib-base`` to your Python path.

#. Add ``mote`` to your ``INSTALLED_APPS`` setting.

#. Register the URL pattern ``url(r"^mote/", include("mote.urls", namespace="mote"))``.

Update the template loaders to include ``mote.loaders.app_directories.Loader``.
When defining custom loaders you may also be required to set the ``APP_DIRS`` template option to ``False``.

A sample ``TEMPLATES`` for a simple Django app typically has this form:

.. code-block:: py

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": False,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "mote.loaders.app_directories.Loader",
                    "django.template.loaders.app_directories.Loader",
                ]
            },
        },
    ]

    # Greatly speed up rendering during development
    if DEBUG:
        loaders = TEMPLATES[0]["OPTIONS"]["loaders"]
        TEMPLATES[0]["OPTIONS"]["loaders"] = \
            [("mote.loaders.cached.Loader", loaders)]

You may now start the Django instance and browse to
``http://localhost:8000/mote``. The only available pattern library at this
point is the base library.

Settings
--------

The ``MOTE`` setting controls Mote' operation. It is a dictionary:

.. code-block:: py

    MOTE = {
        "project": "myproject",
        "directories": ["/path/to/pattern-lib-one", "/path/to/pattern-lib-two"]
    }

``project`` is only required when using the Django API. See the API section for
more information.

``directories`` tells Mote where to find the pattern libraries. Pattern libraries
that are packaged as Django Apps are automatically included. Note the directory
declaration must not include the ``mote`` subdirectory, but the actual directory
on the filesystem must. In our example there must therefore exist a directory
``/path/to/pattern-lib-one/mote/``.

