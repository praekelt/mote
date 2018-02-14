API
###

.. contents::

Mote provides an in-template, full RESTful and Javascript API.

In-template
-----------

You may call any pattern from a Django template. For our example we have a
button pattern:

.. code-block:: html+django

    {% load mote_tags %}

    <a class="{{ class }}">{{ text }}</a>

This button pattern has default data:

.. code-block:: yaml

    text: Lorem ipsum dolor
    class: plain

You may render this button in your template:

.. code-block:: html+django

    {% load mote_tags %}
    {% render "project.browser.atoms.button" %}

You may refer to the project in context using ``self``. This is recommended
practice because it makes it easy to roll out new versions of a pattern
library. For example, if you create the pattern library ``projectv2`` then
you would have to change the name *everywhere*. Using ``self`` avoids this.:

.. code-block:: html+django

    {% load mote_tags %}
    {% render "self.browser.atoms.button" %}

Using ``self``  requires you to declare ``MOTE = {"project": callable_or_string}`` to tell
Mote what project is in context. ``callable_or_string`` takes ``request`` as parameter:

.. code-block:: python

    MOTE = {"project": lambda request: "project"}

You may partially or fully override the button data. Note how you do not have to redeclare
the entire dictionary - Mote will deep merge your values with the default values:

.. code-block:: html+django

    {% load mote_tags %}
    {% render "project.browser.atoms.button" '{"text": "My label"}' %}

You may even use template variables:

.. code-block:: html+django

    {% load mote_tags %}
    {% render "project.browser.atoms.button" '{"text": "{{ foo }}"}' %}

The variable called ``element`` is special. It allows you to relatively lookup
other patterns.  In this example our button pattern also renders one of its sibling
patterns ``anchor``. It's a very artificial example but illustrates the usage.

Let's extend the button pattern to render a sibling.:

.. code-block:: html+django

    {% load mote_tags %}

    <a class="{{ class }}">{{ text }}</a>
    {% render sibling %}

Specify a sibling by a relative lookup.:

.. code-block:: html+django

    {% load mote_tags %}
    {% render "project.browser.atoms.button" '{"sibling": "{{ element.pattern.anchor.dotted_name }}"}' %}

Defining a dictionary in a template tag quickly becomes unwieldy. To combat this you may define an external
template to assemble a data structure through XML. See https://github.com/martinblech/xmltodict
for tips on how to construct the XML.

button.xml file:

.. code-block:: html+django

    <button>
        <text>I have access to context variable {{ foo }}</text>
    </button>

And here we use it. Note the outermost XML tag is not part of the ``button`` dictionary.:

.. code-block:: html+django

    {% load mote_tags %}
    {% get_element_data "button.xml" as button %}
    {% render "project.browser.atoms.button" button %}

RESTful
-------

You may call a pattern by URL::

    /mote/api/project/browser/atoms/button/

This URL accepts a URL encoded JSON parameter which partially or fully overrides
the button data::

    /mote/api/project/browser/atoms/button/?data=%7B%22text%22%3A+%22Awesome%22%7D

Javascript
----------

That is way too ugly and inefficient! Imagine your page has to load 10 patterns
- that's 10 requests. To solve this Mote provides a Javascript class to
multiplex requests and simplify the calling interface:

.. code-block:: html

    <div id="target"></div>

    <script type="text/javascript" src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}mote/js/api.js"></script>

    <script type="text/javascript">
    $(document).ready(function() {
        var mote_api = new MoteAPI('/mote/api/', 'project');
        mote_api.push(
            'self.browser.atoms.button',
            {'text': 'Awesome'},
            '#target',
            function(result) { alert('Loaded!'); }
         );
         mote_api.push(
            'explicit-patternlib.browser.atoms.button',
            {'text': 'Awesome again'},
            '#target'
         );
         mote_api.run();
    });
    </script>

The MoteAPI contructor takes two parameters, ``api_root`` (required) and
``project_id`` (optional). ``project_id`` is used to resolve ``self`` to the
correct project but it may be ommited, in which case Mote, depending on the ``MOTE``
setting, attempts to resolve to the correct project. It is recommended to
always pass a ``project_id``.

``push`` parameters:
    #. url - the API endpoint.
    #. data - optional dictionary to override pattern data.
    #. selector - optional CSS selector to fill with the rendered pattern.
    #. callback - optional callback. ``result`` is a JSON object. ``json`` and ``rendered`` are the most used keys in ``result``.
