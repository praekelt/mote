Patterns
########

.. contents::

A pattern in Mote is a representation of a self-contained unit of reusable interface.

Each pattern is displayed in the Mote Explorer as a resizable iframe, and can be viewed on its own page in isolation.

A pattern contains a minimal set of files.

::

    root
    └── example-pattern
        ├── element.html
        ├── data.yaml (optional)
        ├── metadata.yaml (optional)
        ├── usage.html or usage.md or usage.rst (optional)
        └── variations (optional directory)


For the sake of example, from here we will be referring to the "anchor" pattern
and we'll go through the process of creating a pattern step-by-step.

Anchor example
--------------

element.html
************

A pattern is written in the Mote Templating Language (MTL), a subset of the popular
Jinja templating language.

.. code-block:: html+django

    {% load mote_tags %}

    <a>{{ text }}</a>

data.yaml
*********

A pattern usually needs data to be useful. The data file provides both the
data structure and default values.

.. code-block:: yaml

    text: Anchor text

metadata.yaml
*************

Information that cannot be inferred from the naming conventions resides in the
metadata file.

.. code-block:: yaml

    title: A Very Simple Anchor
    description: This is the simplest possible anchor.

Re-use example
--------------

A pattern may re-use any other pattern to do its rendering. This trivial example
illustrates the technique.

element.html
************

.. code-block:: html+django

    {% load mote_tags %}

    {% render "project.browser.atoms.anchor" data %}

How data.yaml works
-------------------

The most powerful and difficult part of Mote is understanding how data.yaml works,
and how to provide partial user-specified data to a pattern so it renders correctly.

Let's start with a simple data file:

.. code-block:: yaml

    text: Anchor text
    attrs:
        ref: /link
        ata-foo: bar

Mote interprets the data file and makes certain variables available in element.html,
in this case ``data``, ``text`` and ``attrs``. Making the first-depth variables
directly available is a concious design decision because it leads to cleaner templates.

The data structure may grow arbitrarily deep but typically they grow to maximum four levels.
Anything more and the patterns themselves are probably too complex. We explore that
in the pattern composition section.

In this case ``element.html`` is slightly more complex:

.. code-block:: html+django

    {% load mote_tags %}

    <a href="{{ attrs.href }}" data-foo="{{ attrs.foo }}">{{ text }}</a>

If you really want to make the element handle all data variations then use
a for loop:

.. code-block:: html+django

    {% load mote_tags %}

    <a {% for k, v in attrs.items %} {{ k }}="{{ v }}" {% endfor %}>
        {{ text }}
    </a>

The pattern renders as:

.. code-block:: html

    <a href="/link" data-foo="bar">Anchor text</a>

That's not particularly useful because all links don't go to ``/link``, so let's
provide user-defined data to the pattern. At this stage we are not concerned with
*how* to pass user-defined data to the pattern but with *what* this data looks like.

.. code-block:: yaml

    text: Google
    attrs:
        href: http://www.google.com

Yields:

.. code-block:: html

    <a href="http://www.google.com" data-foo="bar">Google</a>

Notice how ``data-foo`` is still present even though it is not part of the
user-defined data. This is because Mote performs a *deep merge* of data, meaning
you need only declare the items you want to provide data for. This is incredibly
useful if your default data is large because it would be cumbersome to have to
redeclare the entire data structure in your user-defined data.

The attrs approach is also extensible by allowing you to declare items the
pattern has no knowledge of, in this case a ``target`` attribute.

.. code-block:: yaml

    text: Google
    attrs:
        href: http://www.google.com
        target: _blank

Yields:

.. code-block:: html

    <a href="http://www.google.com" data-foo="bar" target="_blank">Google</a>

Composite patterns
------------------

The major benefit of a pattern library is to provide a set of *reusable* patterns.
This is best illustrated through an example: an ``anchor`` pattern re-using a
``text`` pattern.

The text pattern:

.. code-block:: yaml

    text: Simple text

.. code-block:: html+django

    {{ text }}

The composite anchor pattern:

.. code-block:: yaml

    children:
        text:
            id: project.browser.atoms.text
            value: Anchor text one
    attrs:
        href: #

.. code-block:: html+django

    {% load mote_tags %}

    <a {% for k, v in attrs.items %} {{ k }}="{{ v }}" {% endfor %}>
        {% for child in children.values %}
            {% render child %}
        {% endfor %}
    </a>

The anchor pattern is now fully extensible  - it takes an arbitrary number of
attrs and an arbitrary number of children inside it, with the text pattern
being the only child by default.

User-defined data is now a combination of the text pattern'ss data and the anchor's
data:

.. code-block:: yaml

    children:
        text:
            value: Google
    attrs:
        href: http://www.google.com

Yields:

.. code-block:: html

    <a href="http://www.google.com" data-foo="bar">Google</a>

Note that once again only a subset of the full data needs to be considered
for user-defined data.

Documenting patterns
--------------------

A pattern may be documented through either HTML, markdown or restructured text.
Create either a ``usage.html``, ``usage.md`` or ``usage.rst`` file in the pattern
root to surface documentation through the Mote Explorer.

Variations
----------

A variation is a pattern that is so similar to an existing pattern that it does not warrant
to be a pattern itself.

A variation has exactly the same structure and rules as a pattern. Place
pattern in the variations directory of an existing pattern and it is made
available as a variation, not a pattern.

Referencing a pattern or variation
----------------------------------

Mote uses a dotted name notation to resolve patterns and variations by name. A
pattern resides in the directory
`mote/projects/project/library/browser/atoms/anchor` is named
`project.browser.atoms.anchor`. Similarly, a variation that resides in the directory
`mote/projects/project/library/browser/atoms/anchor/variations/alert` is named
`project.browser.atoms.anchor.alert`.

The name of the project should nearly always be replaced by ``self``. This
reserved word resolves to the project currently in scope and is useful when
basing entire pattern libraries on other pattern libraries.
