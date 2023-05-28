pytest-xvfb changelog
=====================

v3.0.0 (unreleased)
-------------------

- Support for Python 3.5 and 3.6 is now dropped, while official support for 3.9,
  3.10 and 3.11 was added (with no code chances required).
- The ``Xvfb`` instance is now no longer saved in pytest's ``config`` object as
  ``config.xvfb`` anymore, and only available via the ``xvfb`` fixture.
- Xvfb is now shut down as late as possible (via an ``atexit`` hook registered
  at import time), seemingly avoiding errors such as
  "XIO: fatal IO error 0 (Success)".
- Code reformatting using black/shed.

v2.0.0
------

- PyVirtualDisplay 1.3 and newer is now supported, support for older versions
  was dropped.
- Support for Python 2.7, 3.3 and 3.4 is now dropped.
- Support for Python 3.6, 3.7 and 3.8 was added (no code changes required).
- Xvfb is now not started anymore in the xdist master process.

v1.2.0
------

- ``Item.get_closest_marker`` is now used, which restores compatibility with
  pytest 4.1.0 and requires pytest 3.6.0 or newer.

v1.1.0
------

- The ``xvfb_args`` option is now a single line parsed with ``shlex.split``.
- The ``XvfbExitedError`` exception now includes stdout and stderr.

v1.0.0
------

- Use `PyVirtualDisplay`_ to start/stop Xvfb
- Show a warning on Linux if Xvfb is unavailable

.. _PyVirtualDisplay: https://pypi.python.org/pypi/PyVirtualDisplay

v0.3.0
------

- Add a new ``xvfb_xauth`` setting which creates an ``XAUTHORITY`` file.

v0.2.1
------

- The temporary directory searched for logfiles is now hardcoded to /tmp
  as that's what X11 does as well.

v0.2.0
------

- The ``no_xvfb``-marker is now registered automatically so pytest doesn't fail
  when run with ``--strict``.
- The ``xvfb`` fixture is now session-scoped.

v0.1.0
------

- Initial release
