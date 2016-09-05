# -*- coding: utf-8 -*-

import os
import re
import time
import os.path
import fnmatch
import subprocess

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
        self.display = None
        self._old_display = None
        self._proc = None

    def start(self):
        self._old_display = os.environ.get('DISPLAY', None)
        self.display = self._get_free_display()
        display_str = ':{}'.format(self.display)
        os.environ['DISPLAY'] = display_str

        cmd = ['Xvfb', display_str, '-screen', '0',
               '{}x{}x{}'.format(self.width, self.height, self.colordepth)]
        cmd.extend(self.args)
        self._proc = subprocess.Popen(cmd)

        time.sleep(0.1)  # Give Xvfb a bit of time to start/fail
        ret = self._proc.poll()

        if ret is not None:
            raise XvfbExitedError("Xvfb exited with exit code {0}".format(ret))

    def stop(self):
        if self._old_display is None:
            del os.environ['DISPLAY']
        else:
            os.environ['DISPLAY'] == self._old_display
        try:
            self._proc.terminate()
            self._proc.wait()
        except OSError:
            pass

    def _get_free_display(self):
        pattern = '.X*-lock'
        lockfiles = fnmatch.filter(os.listdir('/tmp'), pattern)
        existing_displays = [int(re.match('^\.X(\d+)-lock$', name).group(1))
                             for name in lockfiles]
        if existing_displays:
            return max(existing_displays) + 1
        else:
            return 0


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
                  type='linelist')


def pytest_configure(config):
    if config.getoption('--no-xvfb') or not xvfb_available():
        config.xvfb = None
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
