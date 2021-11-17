==========================================
Directory Schema Checker
==========================================

.. image:: https://img.shields.io/pypi/v/dirschema.svg
        :target: https://pypi.python.org/pypi/dirschema

.. image:: https://pyup.io/repos/github/mozbhearsum/dirschema/shield.svg
     :target: https://pyup.io/repos/github/mozbhearsum/dirschema/
     :alt: Updates


Linter to ensure a directory complies with a schema.

* Free software: MPL2

Quickstart
----------

Define a schema:

::

    {
        "allow_extra_files": true,
        "allow_extra_dirs": true,
        "files": {
            "HISTORY.rst": {},
            "MANIFEST.in": {
                "contains": [
                    "include pyproject.toml",
                    "include setup.py",
                    "recursive-include src *",
                    "recursive-include tests *"
                ]
            },
            "README.rst": {},
            "pyproject.toml": {},
            "setup.py": {},
            "tox.ini": {},
            ".taskcluster.yml": {}
        },
        "dirs": {
            "requirements": {
                "allow_extra_files": false,
                "allow_extra_dirs": false,
                "files": {
                    "base.in": {},
                    "base.txt": {},
                    "test.in": {},
                    "test.txt": {},
                    "local.in": {},
                    "local.txt": {}
                }
            },
            "src": {
                "allow_extra_files": false,
                "allow_extra_dirs": true
            },
            "tests": {
                "allow_extra_files": true,
                "allow_extra_dirs": true
            }
        }
    }

Create a directory structure:

::

    $ find sample/
    sample
    sample/HISTORY.rst
    sample/src
    sample/setup.py
    sample/pyproject.toml
    sample/requirements
    sample/requirements/base.in
    sample/requirements/local.txt
    sample/requirements/base.txt
    sample/requirements/local.in
    sample/requirements/test.txt
    sample/requirements/test.in
    sample/MANIFEST.in
    sample/.taskcluster.yml
    sample/tox.ini
    sample/README.rst
    $ cat sample/MANIFEST.in
    include pyproject.toml
    include setup.py
    recursive-include src *
    $ dirschema sample.json sample/
    Checking sample/…
    
    Results
    *******
    sample/: Has errors
    missing dir in root directory: tests
    MANIFEST.in is missing required string: 'recursive-include tests *'

    $

Fix the errors, and run it again:

::

    $ echo "recursive-include tests *" >> sample/MANIFEST.in
    $ mkdir sample/tests
    $ dirschema sample.json sample/
    Checking sample/…

    Results
    *******
    sample/: Success!

    $

Features
--------

* Require specified files to exist, and optionally have specific contents
* Require specified directories to exist
* Allow or deny files outside of the schema to exist
* Directory structure can be checked as deep as desired
* Check a local directory or a Github repository

FAQ
---
* Why?
* Why not JSON Schema?

Credits
-------
