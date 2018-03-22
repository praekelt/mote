Directory structure
###################

Mote embraces convention over configuration and infers much from a directory tree.

A collection of pattern libraries are rooted at a ``mote`` directory and follow
this structure:

::

    .
    └── mote
        └── projects
            └── project
                └── library
                    └── aspect
                        └── patterns
                            └── category
                                └── pattern
                                    └── variations


A more complex directory structure consisting of multiple projects, aspects and
pattern categories following the Atomic Design convention.

::

    .
    └── mote
        └── projects
            ├── project1
            │   ├── library
            │   │   └── emails
            │   │       └── patterns
            │   │           ├── atoms
            │   │           ├── molecules
            │   │           ├── organisms
            │   │           ├── pages
            │   │           └── templates
            │   ├── library
            │   │   └── intranet
            │   │       └── patterns
            │   │           ├── atoms
            │   │           ├── molecules
            │   │           ├── organisms
            │   │           ├── pages
            │   │           └── templates
            │   └── library
            │       └── browser
            │           └── patterns
            │               ├── atoms
            │               ├── molecules
            │               ├── organisms
            │               ├── pages
            │               └── templates
            └── project2
                ├── library
                │   └── emails
                │       └── patterns
                │           ├── atoms
                │           ├── molecules
                │           ├── organisms
                │           ├── pages
                │           └── templates
                ├── library
                │   └── intranet
                │       └── patterns
                │           ├── atoms
                │           ├── molecules
                │           ├── organisms
                │           ├── pages
                │           └── templates
                └── library
                    └── browser
                        └── patterns
                            ├── atoms
                            ├── molecules
                            ├── organisms
                            ├── pages
                            └── templates

