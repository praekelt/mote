####
Installation
####
To install the latest **stable release**, run:

.. code-block:: shell

    $ pip install mote-prk


Alternatively, for the latest **development release**, run:

.. code-block:: bash

    $ pip install -e git+https://github.com/praekelt/mote.git@develop#egg=mote


====
Requirements
====
Mote works on the following environments:

* Django 1.9.x & Python 2.7.x
* Django 1.10.x & Python 2.7.x/3.5.x
* Django 1.11.x & Python 2.7.x/3.5.x

====
Configuring Django
====

Configuring settings.py
====
Add Mote to your ``INSTALLED_APPS``.

.. code-block:: python

    INSTALLED_APPS = (
        "mote",
    )

Next, you must configure ``TEMPLATES`` as follows:

.. code-block:: python

    TEMPLATES = [
        {
            "APP_DIRS": False,
            "OPTIONS": {
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "mote.loaders.app_directories.Loader",
                    "django.template.loaders.app_directories.Loader",
                ]
            },
        },
    ]


Configuring urls.py
====
The Mote Explorer interface may be exposed on a route by adding the following to ``urls.py``:

.. code-block:: python

    from django.conf.urls import url, include

    urlpatterns = [
        url(
            r"^mote/",
            include("mote.urls", namespace="mote")
        ),
    ]

Once configured, you may access the Mote Explorer at ``http://<mydomain>/mote``.
