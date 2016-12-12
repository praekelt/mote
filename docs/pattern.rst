Creating a Mote Pattern
#######################

A pattern in Mote is a representation of a self-contained unit of reusable interface.

Each pattern is displayed in the Mote interface as a resizable iframe, and can be viewed on its own page in isolation.

Mote expects the following directory and file structure per pattern:

::

    button
    ├── element.html
    ├── index.html
    ├── json
    │   └── data.json
    └── metadata.json

Have a look at this Gist_ for an example of a minimally functional set of content to get a pattern working in Mote.

.. _Gist: https://gist.github.com/CSergienko/023b0066c4dedf74c98ff082d81e478c

For the sake of example, from here we will be referring to the "button" component and we'll go through the process of creating a pattern step-by-step.

Metadata
-------------

This file should contain bits of information about the particular pattern, such as its title and description.

.. code-block:: json

    // button/metadata.json
    {
        "title": "Button",
        "description": "It's a standard HTML button."
    }

Pattern Markup
------------

This is where the markup of the component resides.

.. code-block:: html

    <!-- button/element.html -->
    {% load mote_tags %}

    <button class="Button">I am a button</button>

Congratulations! Your pattern should be appearing in the Mote interface.

Pattern Documentation
----------

Ideally, each component should come with some usage examples. Simple components, such as our "Button" component, won't require much of this, but it becomes increasingly necessary as pattern complexity increases.

As of the current version of Mote, this requires a bit of copying and pasting.

.. code-block:: html

    <!-- button/index.html -->
    {% extends "mote/element/index.html" %}
    {% load mote_tags %}

    {% block codeblock %}
    <div class="sg-code-block">
        <h4 class="title">
            Button Default State
        </h4>
        <div class="description">
            Code Block Description
        </div>
        <div class="code-example">
            <pre>
                <code class="language-markup">
                    <xmp>

    <button class="Button">I am a button</button>

                    </xmp>
                </code>
            </pre>
        </div>
        <!-- code-example -->
        </div>
    <!-- sg-code-block -->
    {% endblock %}

It is worth noting that the indentation of the button inside of the ``code-example`` tag is not an accident. Indentation is treated as part of the pre-formatted text.

A useful trick is to use ``{% render_element original_element %}`` in place of manually writing the markup into the code block. Similarly, one can also do this for variations, explained further down in this document.

Dummy Data
--------------

When composing complex interfaces out of various patterns, it becomes necessary to inject "dummy data". This can be used to emulate content, or to apply states and additional styles to components.

.. code-block:: json

    // button/json/data.json
    {
        "Button": {
            "text": "I am a button",
            "modifiers": "Button--big Button--red"
        }
    }

Using Dummy Data
################

Once the dummy data has been created, it is can be consumed in ``element.html`` like so:

.. code-block:: html

    <!-- button/element.html -->
    {% load mote_tags %}

    <button class="Button {{ element.json.data.Button.modifiers }}">{{ element.json.data.Button.text }}</button>

Note that ``element.json.data`` refers to the name of the JSON file, and ``element.json.data.Button`` refers to the "Button" object inside of the JSON.

Obviously, this is a rather verbose syntax, and can get a bit overwhelming as the depth of the JSON increases in more complex use cases.

Therefore, it is strongly recommended to use the ``{% mask %}`` tag as it carries benefits beyond terse code. See the following example:

.. code-block:: html

    <!-- button/element.html -->
    {% load mote_tags %}

    {% mask element.json.data.Button as "button" %}

    <button class="Button {{ button.modifiers }}">{{ button.text }}</button>

Creating variations of patterns
###############################

A single pattern may require numerous variations to fully demonstrate and document its usage. Fortunately, Mote makes this easy for us.

In the ``button`` pattern's directory, create a new directory called ``variations``, with a subdirectory called ``secondary`` so that your file tree looks as follows:

::

    button
    ├── element.html
    ├── index.html
    ├── json
    │   └── data.json
    │── variations
    │   └── secondary
    └── metadata.json

Next, copy the json directory from the parent button into the variation, like so:

.. code-block:: json

    // button/variations/secondary/json/data.json
    {
        "Button": {
            "modifiers": "Button--secondary"
        }
    }

Once done, create an ``element.html`` for the variation, the contents of which should look something like this:

.. code-block:: html

    <!-- button/variations/secondary/element.html -->
    {% load mote_tags %}

    {% mask element.json.data.Button as "button" %}

    {% render_element original_element button=button %}

As the code suggests, this will render the original button, and perform a deep merge of the dummy data to override only the "modifiers" key, thus creating a variation.

If you go and edit the original button's markup, it will reflect throughout all its variations as well.

Elsewhere in Mote, you may now also directly render a variation like so: ``{% render_element element.aspect.atoms.button.secondary %}``.

Pattern Composition
###################

We have our Button component, and it's consuming dummy data. This is great, because we can now reuse the Button component anywhere and inject whatever content or classes we want without having to touch the markup again.

Let's assume you have a ButtonGroup component which needs to use the Button component. It would look something like this:

.. code-block:: json

    // button-group/json/data.json
    {
    "ButtonGroup": {
            "items": [
                {
                    "text": "Submit",
                    "modifiers": "Button--big Button--blue"
                },
                {
                    "text": "Reset",
                    "modifiers": "Button--big Button--red"
                }
            ]
        }
    }

.. code-block:: html

    <!-- button-group/element.html -->
    {% load mote_tags %}

    {% mask element.json.data.ButtonGroup as "buttonGroup" %}

    <ul class="ButtonGroup">
        {% for item in buttonGroup.items %}
            <li class="ButtonGroup-item">
                {% render_element element.aspect.atoms.button button=item %}
            </li>
        {% endfor %}
    </ul>

You should now have two buttons with different classes and text.

But again, we have a similar situation with verbose code when we're calling ``element.aspect.atoms.button``. Fortunately, there is a simple workaround to this, in the ``{% with %}`` tag:

.. code-block:: html

    <!-- button-group/element.html -->
    {% load mote_tags %}

    {% mask element.json.data.ButtonGroup as "buttonGroup" %}

    {% with element.aspect.atoms as atoms %}
        <ul class="ButtonGroup">
            {% for item in buttonGroup.items %}
                <li class="ButtonGroup-item">
                    {% render_element atoms.button button=item %}
                </li>
            {% endfor %}
        </ul>
    {% endwith %}
