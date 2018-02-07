pytest-xvfb changelog
=====================

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
