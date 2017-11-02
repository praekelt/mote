####
Useful Patterns
####

Attributes
====

In many cases, it is useful to be able to pass an element attributes, be they an id, data attributes, and so on.

This pattern makes it easy to do so by taking a Django dictionary and turning the keys and values into HTML attributes in a manner
which is generic and as clean as possible.

**element.html**

.. code-block:: html+django

    <span {% for k, v in attrs.items %}{{ k }}="{{ v }}" {% endfor %}></span>


**data.yaml**

.. code-block:: yaml

    attrs:
        id: foo
        aria-hidden: true
        role="presentation"

**Output**

.. code-block:: html

    <span id="foo" aria-hidden="true" role="presentation" ></span>

Classes
====

Whilst ``class`` is an attribute, it is a special one. Some classes are conditional, such as indicating state or behaving as a hook for JS.

This pattern maps well to methodologies such as BEM, and makes it easy to override individual classes if necessary as opposed to the entire attribute.

**element.html**

.. code-block:: html+django

    <button class="{% for class in classes.values %}{{ class }} {% endfor %}"></button>

**data.yaml**

.. code-block:: yaml

    classes:
        main: button
        style: button-primary
        state: is-active
        js: js-modal-trigger

**Output**

.. code-block:: html

    <button class="button button-primary is-active js-modal-trigger "></button>

