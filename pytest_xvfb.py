# -*- coding: utf-8 -*-

import os
import re
import time
import os.path
import fnmatch
import hashlib
import tempfile
import subprocess
import sys

import pyvirtualdisplay

import pytest


def xvfb_available():
    # http://stackoverflow.com/a/28909933/2085149
    return any(
        os.access(os.path.join(path, 'Xvfb'), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


class XvfbExitedError(Exception):

    pass


class Xvfb(object):

    def __init__(self, config):
        self.width = int(config.getini('xvfb_width'))
        self.height = int(config.getini('xvfb_height'))
        self.colordepth = int(config.getini('xvfb_colordepth'))
        self.args = config.getini('xvfb_args') or []
        self.xauth = config.getini('xvfb_xauth')
        self.display = None
        self._virtual_display = None

    def start(self):
        self._virtual_display = pyvirtualdisplay.Display(
            backend='xvfb', size=(self.width, self.height),
            color_depth=self.colordepth, use_xauth=self.xauth)
        self._virtual_display.cmd.extend(self.args)
        self._virtual_display.start()
        self.display = self._virtual_display.display

        if not self._virtual_display.is_alive():
            ret = self._virtual_display.return_code
            self._virtual_display.wait()  # collect outputs
            stdout = self._virtual_display.stdout
            stderr = self._virtual_display.stderr
            raise XvfbExitedError("Xvfb exited with exit code {0}\nXvfb stdout:\n    {1}\nXvfb stderr:\n    {2}".format(
                ret,
                '\n    '.join(stdout.splitlines()),
                '\n    '.join(stderr.splitlines())))

    def stop(self):
        self._virtual_display.stop()


def pytest_addoption(parser):
    group = parser.getgroup('xvfb')
    group.addoption(
        '--no-xvfb',
        action='store_true',
        help='Disable Xvfb for tests.'
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
    if config.getoption('--no-xvfb') or not xvfb_available():
        config.xvfb = None
        if (sys.platform.startswith('linux')
                and 'DISPLAY' in os.environ
                and not config.getoption('--no-xvfb')):
            print('pytest-xvfb could not find Xvfb. '
                  'You can install it to prevent windows from being shown.')
    else:
        config.xvfb = Xvfb(config)
        config.xvfb.start()
    config.addinivalue_line("markers", "no_xvfb: Skip test when using Xvfb")


def pytest_unconfigure(config):
    if getattr(config, 'xvfb', None) is not None:
        config.xvfb.stop()


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_marker('no_xvfb') and item.config.xvfb is not None:
            skipif_marker = pytest.mark.skipif(
                True, reason="Skipped with Xvfb")
            item.add_marker(skipif_marker)


@pytest.fixture(scope='session')
def xvfb(pytestconfig):
    return pytestconfig.xvfb
