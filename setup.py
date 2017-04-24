import os
from setuptools import setup, find_packages


def get_version(fname):
    '''Extracts __version__ from {fname}'''
    import re
    verstrline = open(fname, "rt").read()
    mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", verstrline, re.M)
    if mob:
        return mob.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (fname,))


setup(
    name="mote-prk",
    version=get_version('mote/__init__.py'),
    description="Mote - the pattern library framework.",
    long_description = open("README.rst", "r").read() + open("AUTHORS.rst", "r").read() + open("CHANGELOG.rst", "r").read(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        "django",
        "beautifulsoup4",
        "six",
        "djangorestframework-jwt",
        "djangorestframework",
        "xmltodict",
        "PyYAML"
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
