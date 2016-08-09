pytest-xvfb changelog
=====================

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
