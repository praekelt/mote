Creating a Mote Pattern
#######################

A pattern in Mote is a representation of a self-contained unit of reusable interface.

Each pattern is displayed in the Mote interface as a resizable iframe, and can be viewed on its own page in isolation.

Mote expects the following directory and file structure per pattern:

::

    example-pattern
    ├── element.html
    ├── index.html
    ├── json
    │   └── data.json
    └── metadata.json

For the sake of example, from here we will be referring to the "button" component in the below examples.

metadata.json
-------------

This file should contain bits of information about the particular pattern, such as its title and description.

.. code-block:: json

    {
        "title": "Button",
        "description": "It's a standard HTML button."
    }

element.html
------------

This is where the markup of the component resides.

.. code-block:: html

    {% load mote_tags %}

    <button class="Button">I am a button</button>

Congratulations! Your pattern should be appearing in the Mote interface.

index.html
----------

Ideally, each component should come with some usage examples. Simple components, such as our "Button" component, won't require much of this, but it becomes increasingly necessary as pattern complexity increases.

As of the current version of Mote, this requires a bit of copying and pasting.

.. code-block:: html

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

json/data.json
--------------
