import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name="mote",
    version="0.1",
    description="Core of the Mote styleguide framework.",
    long_description=read('README.rst'),
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
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
