======
reiter
======

Wrapper for Python iterators and iterables that implements a list-like random-access interface by caching retrieved items for later reuse.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/reiter.svg
   :target: https://badge.fury.io/py/reiter
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/reiter/badge/?version=latest
   :target: https://reiter.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/lapets/reiter/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/lapets/reiter/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/lapets/reiter/badge.svg?branch=main
   :target: https://coveralls.io/github/lapets/reiter?branch=main
   :alt: Coveralls test coverage summary.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/reiter>`__:

.. code-block:: bash

    python -m pip install reiter

The library can be imported in the usual way:

.. code-block:: python

    import reiter
    from reiter import reiter

Examples
^^^^^^^^

.. |reiter| replace:: ``reiter``
.. _reiter: https://reiter.readthedocs.io/en/0.8.0/_source/reiter.html#reiter.reiter.reiter

This library makes it possible to wrap any `iterator <https://docs.python.org/3/glossary.html#term-iterator>`__ or `iterable <https://docs.python.org/3/glossary.html#term-iterable>`__ object within an interface that enables repeated iteration over -- and random access by index of -- the items contained within that object. A |reiter|_ instance yields the same sequence of items as the wrapped iterator or iterable:

.. code-block:: python

    >>> from reiter import reiter
    >>> xs = iter([1, 2, 3])
    >>> ys = reiter(xs)
    >>> list(ys)
    [1, 2, 3]

.. |iter| replace:: ``iter``
.. _iter: https://docs.python.org/3/library/functions.html#iter

Unlike iterators and some iterable objects (including those that are built-in and those that are user-defined), an instance of the |reiter|_ class *always* allows iteration over its items any number of times. More specifically, every invocation of |iter|_ (explicit or implicit) returns an iterator that begins iteration from the first item found in the originally wrapped iterator or iterable:

.. code-block:: python

    >>> list(iter(ys)), list(iter(ys))
    ([1, 2, 3], [1, 2, 3])
    >>> list(ys), list(ys)
    ([1, 2, 3], [1, 2, 3])

Furthermore, it is also possible to access elements by their index:

.. code-block:: python

    >>> xs = iter([1, 2, 3])
    >>> ys = reiter(xs)
    >>> ys[0], ys[1], ys[2]
    (1, 2, 3)

.. |next| replace:: ``next``
.. _next: https://docs.python.org/3/library/functions.html#next

.. |StopIteration| replace:: ``StopIteration``
.. _StopIteration: https://docs.python.org/3/library/exceptions.html#StopIteration

The built-in Python |next|_ function is also supported, and any attempt to retrieve an item once the sequence of items is exhausted raises the |StopIteration|_ exception in the usual manner:

.. code-block:: python

    >>> xs = reiter(iter([1, 2, 3]))
    >>> next(xs), next(xs), next(xs)
    (1, 2, 3)
    >>> next(xs)
    Traceback (most recent call last):
      ...
    StopIteration

However, all items yielded during iteration can be accessed by their index, and it is also possible to iterate over those items again:

.. code-block:: python

    >>> xs[0], xs[1], xs[2]
    (1, 2, 3)
    >>> [x for x in xs]
    [1, 2, 3]

.. |reiter___getitem__| replace:: ``__getitem__``
.. _reiter___getitem__: https://reiter.readthedocs.io/en/0.8.0/_source/reiter.html#reiter.reiter.reiter.__getitem__

Retrieval of yielded items using slice notation is also supported via the |reiter___getitem__|_ method:

.. code-block:: python

    >>> xs = reiter(iter([1, 2, 3]))
    >>> xs[0:2]
    [1, 2]

.. |reiter_has| replace:: ``has``
.. _reiter_has: https://reiter.readthedocs.io/en/0.8.0/_source/reiter.html#reiter.reiter.reiter.has

.. |reiter_length| replace:: ``length``
.. _reiter_length: https://reiter.readthedocs.io/en/0.8.0/_source/reiter.html#reiter.reiter.reiter.length

Instances of |reiter|_ support additional inspection methods, as well. For example, the |reiter_has|_ method returns a boolean value indicating whether a next item is available and the |reiter_length|_ method returns the length of the sequence of items emitted by the instance (once no more items can be emitted):

.. code-block:: python

    >>> xs = reiter(iter([1, 2, 3]))
    >>> xs.has(), xs.has(), xs.has(), xs.has()
    (True, True, True, False)
    >>> xs.length()
    3

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

    python src/reiter/reiter.py -v

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install .[lint]
    python -m pylint src/reiter

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/lapets/reiter>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/reiter>`__ by a package maintainer. First, install the dependencies required for packaging and publishing:

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
