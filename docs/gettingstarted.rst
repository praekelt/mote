Getting Started
################

.. contents::

Installation
------------

Mote is built using the Django web framework, which means installation is fairly simple
over a wide range of operating systems.

Standalone
**********

Mote is intended to be a standalone library, not a project, but it can indeed be run
by using the test configuration:

::

    - virtualenv ve
    - ./ve/bin/pip install -r mote/tests/requirements/111.txt
    - ./ve/bin/python manage.py migrate --run-syncdb --settings=mote.tests.settings.111
    - ./ve/bin/python manage.py runserver 0.0.0.0:8000 --settings=mote.tests.settings.111

You may now browse to ``http://localhost:8000/mote``. The only available
pattern libraries at this point are the unit test libraries.

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


You may now start the Django instance and browse to
``http://localhost:8000/mote``. The only available pattern library at this
point is the base library.
