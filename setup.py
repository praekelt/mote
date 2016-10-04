import os
from setuptools import setup, find_packages


setup(
    name="mote",
    version="0.1",
    description="Core of the Mote styleguide framework.",
    long_description = open("README.rst", "r").read() + open("AUTHORS.rst", "r").read() + open("CHANGELOG.rst", "r").read(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    packages=find_packages(exclude=["tests*"]),
    zip_safe=False,
    install_requires=[
        "django",
    ],
    tests_require=[
        "tox",
    ],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
