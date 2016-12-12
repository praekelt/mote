Advanced Mote Usage
###################

.. contents::

Using conditional logic to alter pattern output
-----------------------------------------------

As in regular Django templating, you can use whatever logic you deem necessary to construct your patterns and to make them as modular as you require.

For example, consider the following code:

.. code-block:: json

    // button/json/data.json
    {
        "Button": {
            "text": "I am a button",
            "modifiers": "Button--big Button--red",
            "tag": "a"
        }
    }

.. code-block:: html

    // button/element.html
    {% load mote_tags %}

    {% mask element.json.data.Button as "button" %}

    {% if button.tag == "button" %}
        <button class="Button {{ button.modifiers }}">
            {{ button.text }}
        </button>
    {% elif button.tag == "a" %}
        <a href="#" class="Button {{ button.modifiers }}">
            {{ button.text }}
        </a>
    {% else %}
        <input value="{{ button.text }}" class="Button {{ button.modifiers }}" />
    {% endif %}

Thus, by changing a single value in the dummy data, the output of the pattern is altered entirely.
