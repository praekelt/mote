API
###

.. contents::

Mote provides both an in-template and full RESTful API.

In-template
-----------

You may call any element from a Django template. For our example we have a
button element. Note how the `data` variable is automatically created from the
default JSON data:

.. code-block:: html+django

    {% load mote_tags %}

    <a class="{{ data.class }}">{{ data.text }}</a>

This button element has default data described in JSON as:

.. code-block:: json

    {
        "Button": {
            "text": "Lorem ipsum dolor"
            "class": "plain"
        }
    }

You may render this button in your template:

.. code-block:: html+django

    {% load mote_tags %}
    {% render_element "myproject.website.atoms.button" %}

However, you may partially or fully override the button data. Note how you do not have to redeclare
the entire dictionary - Mote will deep merge your values with the default values:

.. code-block:: html+django

    {% load mote_tags %}
    {% render_element "myproject.website.atoms.button" data='{"text": "My label"}' %}

You may even use template variables:

.. code-block:: html+django

    {% load mote_tags %}
    {% render_element "myproject.website.atoms.button" data='{"text": "{{ foo }}"}' %}

The variable called ``element`` is special. It allows you to relatively lookup
other elements.  In this example our button element also renders one of its sibling
elements ``anchor``. It's a very artificial example but illustrates the usage.

Let's extend the button element to render a sibling.:

.. code-block:: html+django

    {% load mote_tags %}

    <a class="{{ data.class }}">{{ data.text }}</a>
    {% render_element data.sibling %}

Specify a sibling by a relative lookup.:

.. code-block:: html+django

    {% load mote_tags %}
    {% render_element "myproject.website.atoms.button" data='{"sibling": "{{ element.pattern.anchor.dotted_name }}"}' %}

Defining a dictionary in a template tag quickly becomes unwieldy. To combat this you may define an external
template to assemble a data structure through XML.

button.xml file:

.. code-block:: html+django

    <button>
        <text>I have access to context variable {{ foo }}</text>
    </button>

And here we use it. Note the outermost XML tag is not part of the `button` dictionary.:

.. code-block:: html+django

    {% get_element_data "button.xml" as button %}
    {% render_element "myproject.website.atoms.button" data=button %}

RESTful
-------

You may call an element by URL::

    /mote/api/myproject/website/atoms/button/

This URL accepts a URL encoded JSON parameter which partially or fully overrides
the button data::

    /mote/api/myproject/website/atoms/button/?button=%2F%3Fbutton%3D%257B%2522text%2522%253A%2522Awesome%2522%257D%22

That is way too ugly and inefficient! Imagine your page has to load 10 elements - that's 10 requests. To
solve this Mote provides a Javascript class to multiplex requests and simplify the calling interface:

.. code-block:: html+django

    <div id="target"></div>

    <script type="text/javascript" src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}mote/js/api.js"></script>

    <script type="text/javascript">
    $(document).ready(function() {
        var mote_api = new MoteAPI('/mote/api/');
        mote_api.push(
            'myproject/website/atoms/button/',
            {'data': {'text': 'Awesome'}},
            '#target',
            function(result) { alert('Loaded!'); }
         );
         mote_api.run();
    });
    </script>

The MoteAPI contructor takes a single parameter, `api_root`.

`push` parameters:
    #. url - the API endpoint.
    #. data - optional dictionary to override element data.
    #. selector - optional CSS selector to fill with the rendered element.
    #. callback - optional callback. `result` is a JSON object. `json` and `rendered` are the most used keys in `result`.

