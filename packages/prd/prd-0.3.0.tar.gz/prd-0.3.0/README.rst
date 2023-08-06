===
prd
===

Idiomatic implementation of a Python function that calculates the product of the items from an iterable.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/prd.svg
   :target: https://badge.fury.io/py/prd
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/prd/badge/?version=latest
   :target: https://prd.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/lapets/prd/actions/workflows/lint-test-cover-docs.yml/badge.svg
   :target: https://github.com/lapets/prd/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/lapets/prd/badge.svg?branch=main
   :target: https://coveralls.io/github/lapets/prd?branch=main
   :alt: Coveralls test coverage summary.

Purpose
-------

.. |sum| replace:: ``sum``
.. _sum: https://docs.python.org/3/library/functions.html#sum

.. |math_sum| replace:: ``math.sum``
.. _math_sum: https://docs.python.org/3/library/math.html#math.prod

.. |functools_reduce| replace:: ``functools.reduce``
.. _functools_reduce: https://docs.python.org/3/library/functools.html#functools.reduce

.. |mul| replace:: ``__mul__``
.. _mul: https://docs.python.org/3/reference/datamodel.html#object.__mul__

A built-in product function that would complement the |sum|_ function was `rejected <https://bugs.python.org/issue1093>`__, and the built-in |math_sum|_ function does not accept iterables that contain values of non-numeric types. This library exports an idiomatic implementation (using |functools_reduce|_) of a product function that can operate on iterables that contain objects of any type for which the multiplication operation is defined (*e.g.*, via a definition of the |mul|_ method). 

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/prd>`__:

.. code-block:: bash

    python -m pip install prd

The library can be imported in the usual ways:

.. code-block:: python

    import prd
    from prd import prd

Examples
^^^^^^^^

.. |operator_mul| replace:: ``operator.mul``
.. _operator_mul: https://docs.python.org/3/library/operator.html#operator.mul

This library exports an idiomatic implementation of a product function (an analog of -- and complement to -- the built-in |sum|_ function). This function applies the built-in multiplication operator |operator_mul|_ to all of the items from the supplied iterable:

.. code-block:: python

    >>> prd([1, 2, 3, 4])
    24
    >>> prd([2])
    2
    >>> prd([1.2, 3.4, 5.6])
    22.848
    >>> prd([])
    1

The function is compatible with objects for which the built-in multiplication operator is defined:

.. code-block:: python

    >>> class var(str):
    ...     def __mul__(self, other):
    ...         return self + ' * ' + other
    ...     def __rmul__(self, other):
    ...         return other + ' * ' + self
    >>> prd([var('b'), var('c'), var('d')], var('a'))
    'a * b * c * d'

The ``start`` parameter and the elements found in the iterable can be of different types. It is only required that the output of the multiplication operation can by multiplied with the next element from the iterable:

.. code-block:: python

    >>> prd([], 'a')
    'a'
    >>> prd([1, 2, 3], 'a')
    'aaaaaa'
    >>> prd(['a', 3], 2)
    'aaaaaa'

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install .[test]
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__:

.. code-block:: bash

    python src/prd/prd.py -v

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install .[lint]
    python -m pylint src/prd

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/lapets/prd>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/prd>`__ by a package maintainer. First, install the dependencies required for packaging and publishing:

.. code-block:: bash

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number):

.. code-block:: bash

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive:

.. code-block:: bash

    rm -rf build dist src/*.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__:

.. code-block:: bash

    python -m twine upload dist/*
