# -*- coding: utf-8 -*-

import os

import pytest

import pytest_xvfb


xauth_available = any(
    os.access(os.path.join(path, 'xauth'), os.X_OK)
    for path in os.environ.get('PATH', '').split(os.pathsep)
)


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
    result.stdout.fnmatch_lines('* could not find Xvfb.*')
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
        "INTERNALERROR> *XvfbExitedError: Xvfb exited with exit code 1",
        "INTERNALERROR> Xvfb stdout:",
        "INTERNALERROR> Xvfb stderr:",
        "INTERNALERROR>     Unrecognized option: -foo",
    ])
    assert 'OSError' not in str(result.stderr)


@pytest.mark.parametrize('args, outcome', [
    ([], '1 passed, 1 skipped'),
    (['--no-xvfb'], '2 passed'),
])
def test_no_xvfb_marker(testdir, args, outcome):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.no_xvfb
        def test_marked():
            pass

        def test_unmarked():
            pass
    """)
    res = testdir.runpytest(*args)
    res.stdout.fnmatch_lines('*= {0}*'.format(outcome))


def test_xvfb_fixture(testdir):
    testdir.makepyfile("""
        import os

        def test_display(xvfb):
            assert ':{}'.format(xvfb.display) == os.environ['DISPLAY']

        def test_screen(xvfb):
            assert xvfb.width == 800
            assert xvfb.height == 600
            assert xvfb.colordepth == 16

        def test_args(xvfb):
            assert xvfb.args == []
    """)
    result = testdir.runpytest()
    assert result.ret == 0


def test_early_display(monkeypatch, testdir):
    """Make sure DISPLAY is set in a session-scoped fixture already."""
    monkeypatch.delenv('DISPLAY')
    testdir.makepyfile("""
        import os
        import pytest

        @pytest.yield_fixture(scope='session', autouse=True)
        def fixt():
            assert 'DISPLAY' in os.environ
            yield

        def test_foo():
            pass
    """)


def test_strict_markers(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.mark.no_xvfb
        def test_marked():
            pass
    """)
    result = testdir.runpytest('--strict')
    assert result.ret == 0


def test_xvfb_session_fixture(testdir):
    """Make sure the xvfb fixture can be used from a session-wide one."""
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='session')
        def fixt(xvfb):
            pass

        def test_fixt(fixt):
            pass
    """)
    result = testdir.runpytest()
    assert result.ret == 0


@pytest.mark.skipif(not xauth_available, reason='no xauth')
def test_xvfb_with_xauth(testdir):
    original_auth = os.environ.get('XAUTHORITY')
    testdir.makeini("""
        [pytest]
        xvfb_xauth = True
    """)
    testdir.makepyfile("""
        import os

        def test_xauth():
            print('\\nXAUTHORITY: ' + os.environ['XAUTHORITY'])
            assert os.path.isfile(os.environ['XAUTHORITY'])
            assert os.access(os.environ['XAUTHORITY'], os.R_OK)
    """)
    result = testdir.runpytest('-s')
    # Get and parse the XAUTHORITY: line
    authline = next(l for l in result.outlines if l.startswith('XAUTHORITY:'))
    authfile = authline.split(' ', 1)[1]

    assert result.ret == 0
    # Make sure the authfile is deleted
    assert not os.path.exists(authfile)
    assert os.environ.get('XAUTHORITY') == original_auth
