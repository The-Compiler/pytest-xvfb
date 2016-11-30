pytest-xvfb
===================================

.. image:: https://travis-ci.org/The-Compiler/pytest-xvfb.svg?branch=master
    :target: https://travis-ci.org/The-Compiler/pytest-xvfb
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/The-Compiler/pytest-xvfb?branch=master
    :target: https://ci.appveyor.com/project/The-Compiler/pytest-xvfb/branch/master
    :alt: See Build Status on AppVeyor

A pytest plugin to run Xvfb for tests.

----

Installation
------------

You can install "`pytest-xvfb`_" via `pip`_ from `PyPI`_::

    $ pip install pytest-xvfb


Usage
-----

With Xvfb and the plugin installed, your testsuite automatically runs with `Xvfb`_. This allows tests to be run without windows popping up during GUI tests or on systems without a display (like a CI).

If Xvfb is not installed, the plugin does not run and your tests will still work as normal. However,
a warning message will print to standard output letting you know that Xvfb is not installed.

If you're currently using ``xvfb-run`` in something like ``.travis.yml``,
simply remove it and install this plugin instead - then you'll also have the
benefits of Xvfb locally.

Features
--------

You can pass ``--no-xvfb`` to explicitly turn off Xvfb (e.g. to visually
inspect a failure).

You can mark tests with ``@pytest.mark.no_xvfb`` to skip them when they're
running with Xvfb.

A ``xvfb`` fixture is available with the following attributes:

- ``width``: The configured width of the screen.
- ``height``: The configured height of the screen.
- ``colordepth``: The configured colordepth of the screen.
- ``args``: The arguments to be passed to Xvfb.
- ``display``: The display number (as int) which is used.

Contributing
------------

Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-xvfb" is free and open source software

Thanks
------

This `pytest`_ plugin was generated with `Cookiecutter`_ along with
`@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.

Thanks to `@cgoldberg`_ for `xvfbwrapper`_ which was the inspiration for this
project.

Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`pytest-xvfb`: https://pypi.python.org/pypi/pytest-xvfb/
.. _`Xvfb`: http://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml
.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`@cgoldberg`: https://github.com/cgoldberg
.. _`xvfbwrapper`: https://github.com/cgoldberg/xvfbwrapper
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/The-Compiler/pytest-xvfb/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
