Getting Started
################

.. contents::

Installation
------------

First, you must add Mote to your project's ``requirements.txt`` file, like so:

::

    mote-prk

Next, you must create a route to Mote in ``urls.py``:

.. code-block:: py

    url(r"^mote/", include("mote.urls", namespace="mote")),

Next, you should update the template loaders to also load templates using the loader ``mote.loaders.app_directories.Loader``.
When defining custom loaders you may also be required to set the ``APP_DIRS`` template option to ``False``.

A sample ``TEMPLATE`` for a default simple Django app may look like this:

.. code-block:: py

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': False,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "mote.loaders.app_directories.Loader",
                    "django.template.loaders.app_directories.Loader",
                ]
            },
        },
    ]

Lastly, ensure that the ``mote/`` root directory is in the parent of one of the ``INSTALLED_APPS``, else mote won't be able to locate it.
This means that if you just set up pattern library using mote and for no other reason, you need to add the project as an application in ``INSTALLED_APPS``.

Congratulations, you may now browse to ```http://localhost:8000/mote``.

Directory Structure
---------------------------------

In the root of your project, you must create a ``mote/`` directory, the minimal structure of which should follow this paradigm:

::

    .
    └── mote
        └── projects
            └── project
                ├── aspect
                │   └── src
                │       ├── patterns
                │       │   ├── category
                │       │       ├── pattern


Below is a more complex directory structure consisting of multiple projects, aspects (think the distinct parts of a project which may require completely different sets of templates, such as website vs. emails), and pattern categories following the Atomic Design convention.

::

    .
    └── mote
        └── projects
            ├── project1
            │   ├── emails
            │   │   └── src
            │   │       └── patterns
            │   │           ├── atoms
            │   │           ├── molecules
            │   │           ├── organisms
            │   │           ├── pages
            │   │           └── templates
            │   ├── intranet
            │   │   └── src
            │   │       └── patterns
            │   │           ├── atoms
            │   │           ├── molecules
            │   │           ├── organisms
            │   │           ├── pages
            │   │           └── templates
            │   └── website
            │       └── src
            │           └── patterns
            │               ├── atoms
            │               ├── molecules
            │               ├── organisms
            │               ├── pages
            │               └── templates
            └── project2
                ├── emails
                │   └── src
                │       └── patterns
                │           ├── atoms
                │           ├── molecules
                │           ├── organisms
                │           ├── pages
                │           └── templates
                ├── intranet
                │   └── src
                │       └── patterns
                │           ├── atoms
                │           ├── molecules
                │           ├── organisms
                │           ├── pages
                │           └── templates
                └── website
                    └── src
                        └── patterns
                            ├── atoms
                            ├── molecules
                            ├── organisms
                            ├── pages
                            └── templates

Pattern Directory Structure
---------------------------

A typical Mote pattern requires the following structure in order to render that component:

::

    category
    └── example-pattern
        ├── element.html
        ├── index.html
        ├── json
        │   └── data.json
        └── metadata.json

Look at this Gist_ to get an idea of what the contents of each file are expected to look like.

.. _Gist: https://gist.github.com/CSergienko/023b0066c4dedf74c98ff082d81e478c
