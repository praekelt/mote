import os
from setuptools import setup, find_packages


setup(
    name="mote-prk",
    version="0.1.1",
    description="Mote - the pattern library framework.",
    long_description = open("README.rst", "r").read() + open("AUTHORS.rst", "r").read() + open("CHANGELOG.rst", "r").read(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    packages=find_packages(),
    zip_safe=True,
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
    include_package_data=True
)
