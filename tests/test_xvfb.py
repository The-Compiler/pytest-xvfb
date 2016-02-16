# -*- coding: utf-8 -*-

import os

import pytest

import pytest_xvfb


@pytest.fixture(autouse=True, scope='session')
def ensure_xvfb():
    if not pytest_xvfb.xvfb_available():
        raise Exception("Tests need Xvfb to run.")


def test_xvfb_available(testdir, monkeypatch):
    monkeypatch.delenv('DISPLAY')
    testdir.makepyfile("""
        import os

        def test_display():
            assert 'DISPLAY' in os.environ
    """)
    result = testdir.runpytest()
    assert result.ret == 0


def test_empty_display(testdir, monkeypatch):
    monkeypatch.setenv('DISPLAY', '')
    testdir.makepyfile("""
        import os

        def test_display():
            assert 'DISPLAY' in os.environ
    """)
    result = testdir.runpytest()
    assert os.environ['DISPLAY'] == ''
    assert result.ret == 0


def test_xvfb_unavailable(testdir, monkeypatch):
    monkeypatch.setenv('PATH', '')
    monkeypatch.setenv('DISPLAY', ':42')
    testdir.makepyfile("""
        import os

        def test_display():
            assert os.environ['DISPLAY'] == ':42'
    """)
    assert os.environ['DISPLAY'] == ':42'
    result = testdir.runpytest()
    assert result.ret == 0


def test_no_xvfb_arg(testdir, monkeypatch):
    monkeypatch.setenv('DISPLAY', ':42')
    testdir.makepyfile("""
        import os

        def test_display():
            assert os.environ['DISPLAY'] == ':42'
    """)
    assert os.environ['DISPLAY'] == ':42'
    result = testdir.runpytest('--no-xvfb')
    assert result.ret == 0


@pytest.mark.parametrize('configured', [True, False])
def test_screen_size(testdir, configured):
    try:
        import tkinter
    except ImportError:
        pytest.importorskip('Tkinter')

    if configured:
        testdir.makeini("""
            [pytest]
            xvfb_width = 1024
            xvfb_height = 768
            xvfb_colordepth = 8
        """)
        expected_width = 1024
        expected_height = 768
        expected_depth = 8
    else:
        expected_width = 800
        expected_height = 600
        expected_depth = 16

    testdir.makepyfile("""
        try:
            import tkinter as tk
        except ImportError:
            import Tkinter as tk

        def test_screen_size():
            root = tk.Tk()
            assert root.winfo_screenwidth() == {width}
            assert root.winfo_screenheight() == {height}
            assert root.winfo_screendepth() == {depth}
    """.format(width=expected_width, height=expected_height,
               depth=expected_depth))
    result = testdir.runpytest()
    assert result.ret == 0


def test_failing_start(testdir, monkeypatch):
    testdir.makeini("""
        [pytest]
        xvfb_args = -foo
    """)
    testdir.makepyfile("""
        def test_none():
            pass
    """)
    result = testdir.runpytest()
    result.stderr.fnmatch_lines([
        "INTERNALERROR> *XvfbExitedError: Xvfb exited with exit code 1"
    ])
    assert 'OSError' not in str(result.stderr)
