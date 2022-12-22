# -*- coding: utf-8 -*-

import os
import os.path
import sys

import pyvirtualdisplay

import pytest


def is_xdist_master(config):
    return (
        config.getoption("dist", "no") != "no" and
        not os.environ.get("PYTEST_XDIST_WORKER")
    )


def xvfb_available():
    # http://stackoverflow.com/a/28909933/2085149
    return any(
        os.access(os.path.join(path, 'Xvfb'), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


class XvfbExitedError(Exception):

    pass


class Xvfb(object):

    def __init__(self, config, backend):
        self.width = int(config.getini('xvfb_width'))
        self.height = int(config.getini('xvfb_height'))
        self.colordepth = int(config.getini('xvfb_colordepth'))
        self.args = config.getini('xvfb_args') or []
        self.xauth = config.getini('xvfb_xauth')
        self.backend = backend
        self.display = None
        self._virtual_display = None

    def start(self):
        self._virtual_display = pyvirtualdisplay.Display(
            backend=self.backend,
            size=(self.width, self.height),
            color_depth=self.colordepth,
            use_xauth=self.xauth,
            extra_args=self.args)
        self._virtual_display.start()
        self.display = self._virtual_display.display
        assert self._virtual_display.is_alive()

    def stop(self):
        if self.display is not None:  # starting worked
            self._virtual_display.stop()


def pytest_addoption(parser):
    group = parser.getgroup('xvfb')
    group.addoption(
        '--no-xvfb',
        action='store_true',
        help='Disable Xvfb for tests.'
    )
    group.addoption(
        '--use-xephyr',
        action='store_true',
        help='Enable Xephyr for tests. Will not work if --no-xvfb'
    )

    parser.addini('xvfb_width', 'Width of the Xvfb display', default='800')
    parser.addini('xvfb_height', 'Height of the Xvfb display', default='600')
    parser.addini('xvfb_colordepth', 'Color depth of the Xvfb display',
                  default='16')
    parser.addini('xvfb_args', 'Additional arguments for Xvfb',
                  type='args')
    parser.addini('xvfb_xauth',
                  'Generate an Xauthority token for Xvfb. Needs xauth.',
                  default=False, type='bool')


def pytest_configure(config):
    no_xvfb = config.getoption('--no-xvfb') or is_xdist_master(config)
    use_xephyr = config.getoption('--use-xephyr')
    if no_xvfb or not xvfb_available():
        config.xvfb = None
        if (sys.platform.startswith('linux')
                and 'DISPLAY' in os.environ
                and not no_xvfb):
            print('pytest-xvfb could not find Xvfb. '
                  'You can install it to prevent windows from being shown.')
    else:
        if use_xephyr:
            config.xvfb = Xvfb(config, backend='xephyr')
        else:
            config.xvfb = Xvfb(config, backend='xvfb')
        config.xvfb.start()
    config.addinivalue_line("markers", "no_xvfb: Skip test when using Xvfb")


def pytest_unconfigure(config):
    if getattr(config, 'xvfb', None) is not None:
        config.xvfb.stop()


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker('no_xvfb') and item.config.xvfb is not None:
            skipif_marker = pytest.mark.skipif(
                True, reason="Skipped with Xvfb")
            item.add_marker(skipif_marker)


@pytest.fixture(scope='session')
def xvfb(pytestconfig):
    return pytestconfig.xvfb
