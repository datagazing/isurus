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




Python class interface to Mako template engine with command line utility

* Free software: MIT license
* Documentation: https://isurus.readthedocs.io.


Features
--------

* Simple command-line interface for interpreting Mako templates
* Easy loading of helper modules into template namespaces
* '#!/usr/bin/env isurus' works for executable templates

Limitations
-----------

Isurus is not particularly efficient with memory use. For various
reasons, it is easiest to read full templates into memory as strings
and this is not a problem for my intended use cases, which are mostly
command-line applications. It may present problems as a general library,
however. In such cases, it might be better to use the original Mako
library interfaces.

Examples
--------

.. code-block:: python

  import isurus
  # input can be either a file name or template as a string
  input = 'asdf <% myvar = 1 %> ${myvar} fdsa ${str(pandas.DataFrame)}'
  template = isurus.Isurus(input)
  template.add_import('pandas')
  # evaluating Isurus object in string context returns interpolated content
  print(template)

At the shell:

.. code-block:: sh

  # on my Mac, pip installs the command line utility in /usr/local/bin
  isurus -h
  isurus some_file.md.mako
  # => creates some_file.md with results of template evaluation

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
