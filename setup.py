from setuptools import setup, find_packages


setup(
    name='mote',
    version='0.1',
    description='Core of the Mote styleguide framework.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    license='BSD',
    url='',
    packages = find_packages(),
    install_requires = [
        'django',
        'tox',
    ],
    include_package_data=True,
    tests_require=[
    ],
    test_suite="",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
