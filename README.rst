======
isurus
======


.. image:: https://img.shields.io/pypi/v/isurus.svg
        :target: https://pypi.python.org/pypi/isurus

.. image:: https://img.shields.io/travis/datagazing/isurus.svg
        :target: https://travis-ci.com/datagazing/isurus

.. image:: https://readthedocs.org/projects/isurus/badge/?version=latest
        :target: https://isurus.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Mako template preprocessor interface/filter


* Free software: MIT license
* Documentation: https://isurus.readthedocs.io.


Features
--------

* Simple command-line interface for interpreting Mako templates
* Easy loading of helper modules into template namespaces

NOTE: Isurus is not particularly efficient with memory use. For
various reasons, it is easiest to read full templates into memory
as strings and this is not a problem for my intended use cases,
which are mostly command-line applications. It may present problems
as a general library, however. In such cases, it might be better
to use the original Mako library interfaces.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
