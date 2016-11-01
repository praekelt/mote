#!/bin/bash

PW=CDX4utXTSc

if [ "X$TRAVIS_BRANCH" == "Xdevelop" -o "X$1" == "Xforce" ]; then
    pip install devpi-client sphinx sphinx_rtd_theme
    devpi use "https://travis:$PW@pypi.praekelt.com/root/praekelt"
    devpi login travis --password="$PW"
    devpi upload --no-vcs --formats sdist --with-docs
else
    echo "Upload skipped, \$TRAVIS_BRANCH is not 'develop'. Or add 'force' parameter."
fi

