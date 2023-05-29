from __future__ import annotations

import os
from typing import Iterator

import pytest
import pyvirtualdisplay

import pytest_xvfb

xauth_available = any(
    os.access(os.path.join(path, "xauth"), os.X_OK)
    for path in os.environ.get("PATH", "").split(os.pathsep)
)


@pytest.fixture(autouse=True, scope="session")
def ensure_xvfb() -> None:
    if not pytest_xvfb.has_executable("Xvfb"):
        raise Exception("Tests need Xvfb to run.")


needs_xephyr = pytest.mark.skipif(
    not pytest_xvfb.has_executable("Xephyr"), reason="Needs Xephyr"
)
needs_xvnc = pytest.mark.skipif(
    not pytest_xvfb.has_executable("Xvnc"), reason="Needs Xvnc"
)


@pytest.fixture(
    params=[
        None,
        "xvfb",
        pytest.param("xephyr", marks=needs_xephyr),
        pytest.param("xvnc", marks=needs_xvnc),
    ]
)
def backend_args(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    monkeypatch.delenv("DISPLAY")
    args = [] if request.param is None else ["--xvfb-backend", request.param]
    if request.param == "xephyr":
        # we need a host display for it... PyVirtualDisplay and Xvfb to the
        # rescue!
        display = pyvirtualdisplay.Display()  # type: ignore[attr-defined]
        display.start()
        yield args
        display.stop()
    else:
        yield args


def test_xvfb_available(pytester: pytest.Pytester, backend_args: list[str]) -> None:
    pytester.makepyfile(
        """
        import os

        def test_display():
            assert 'DISPLAY' in os.environ
    """
    )
    result = pytester.runpytest(*backend_args)
    assert result.ret == 0


def test_empty_display(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, backend_args: list[str]) -> None:
    if backend_args == ["--xvfb-backend", "xephyr"]:
        pytest.skip("Xephyr needs a host display")

    monkeypatch.setenv("DISPLAY", "")
    pytester.makepyfile(
        """
        import os

        def test_display():
            assert 'DISPLAY' in os.environ
    """
    )
    result = pytester.runpytest(*backend_args)
    assert os.environ["DISPLAY"] == ""
    assert result.ret == 0


def test_xvfb_unavailable(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("DISPLAY", ":42")
    pytester.makepyfile(
        """
        import os

        def test_display():
            assert os.environ['DISPLAY'] == ':42'
    """
    )
    assert os.environ["DISPLAY"] == ":42"
    result = pytester.runpytest()
    result.stdout.fnmatch_lines("* could not find Xvfb.*")
    assert result.ret == 0


def test_xvfb_unavailable_explicit(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, backend_args: list[str]) -> None:
    """If an explicitly chosen backend is unavailable: Hard error."""
    if not backend_args:
        pytest.skip("Already tested above")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("DISPLAY", ":42")
    pytester.makepyfile(
        """
        import os

        def test_display():
            assert False  # never run
    """
    )
    assert os.environ["DISPLAY"] == ":42"
    result = pytester.runpytest(*backend_args)
    result.stderr.fnmatch_lines("*xvfb backend * requested but not installed.")
    assert result.ret == pytest.ExitCode.USAGE_ERROR


def test_no_xvfb_arg(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, backend_args: list[str]) -> None:
    monkeypatch.setenv("DISPLAY", ":42")
    pytester.makepyfile(
        """
        import os

        def test_display():
            assert os.environ['DISPLAY'] == ':42'
    """
    )
    assert os.environ["DISPLAY"] == ":42"
    result = pytester.runpytest("--no-xvfb", *backend_args)
    assert result.ret == 0


@pytest.mark.parametrize("configured", [True, False])
def test_screen_size(pytester: pytest.Pytester, configured: bool, backend_args: list[str]) -> None:
    if backend_args == ["--xvfb-backend", "xvnc"]:
        pytest.skip("Seems to be unsupported with Xvnc")

    try:
        import tkinter  # noqa
    except ImportError:
        pytest.importorskip("Tkinter")

    if configured:
        pytester.makeini(
            """
            [pytest]
            xvfb_width = 1024
            xvfb_height = 768
            xvfb_colordepth = 8
        """
        )
        expected_width = 1024
        expected_height = 768
        expected_depth = 8
    else:
        expected_width = 800
        expected_height = 600
        expected_depth = 16

    pytester.makepyfile(
        """
        try:
            import tkinter as tk
        except ImportError:
            import Tkinter as tk

        def test_screen_size():
            root = tk.Tk()
            assert root.winfo_screenwidth() == {width}
            assert root.winfo_screenheight() == {height}
            assert root.winfo_screendepth() == {depth}
    """.format(
            width=expected_width, height=expected_height, depth=expected_depth
        )
    )
    result = pytester.runpytest(*backend_args)
    assert result.ret == 0


def test_failing_start(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, backend_args: list[str]) -> None:
    pytester.makeini(
        """
        [pytest]
        xvfb_args = -foo
    """
    )
    pytester.makepyfile(
        """
        def test_none():
            pass
    """
    )
    result = pytester.runpytest(*backend_args)
    result.stderr.fnmatch_lines(
        [
            "INTERNALERROR> *.XStartError: X* program closed. *",
        ]
    )
    assert "OSError" not in str(result.stderr)


@pytest.mark.parametrize(
    "args, outcome",
    [
        ([], "1 passed, 1 skipped"),
        (["--no-xvfb"], "2 passed"),
    ],
)
def test_no_xvfb_marker(pytester: pytest.Pytester, args: list[str], outcome: str, backend_args: list[str]) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.no_xvfb
        def test_marked():
            pass

        def test_unmarked():
            pass
    """
    )
    res = pytester.runpytest(*args, *backend_args)
    res.stdout.fnmatch_lines(f"*= {outcome}*")


def test_xvfb_fixture(pytester: pytest.Pytester, backend_args: list[str]) -> None:
    pytester.makepyfile(
        """
        import os

        def test_display(xvfb):
            assert ':{}'.format(xvfb.display) == os.environ['DISPLAY']

        def test_screen(xvfb):
            assert xvfb.width == 800
            assert xvfb.height == 600
            assert xvfb.colordepth == 16

        def test_args(xvfb):
            assert xvfb.args == []
    """
    )
    result = pytester.runpytest(*backend_args)
    assert result.ret == 0


def test_early_display(monkeypatch: pytest.MonkeyPatch, pytester: pytest.Pytester, backend_args: list[str]) -> None:
    """Make sure DISPLAY is set in a session-scoped fixture already."""
    pytester.makepyfile(
        """
        import os
        import pytest

        @pytest.yield_fixture(scope='session', autouse=True)
        def fixt():
            assert 'DISPLAY' in os.environ
            yield

        def test_foo():
            pass
    """
    )
    result = pytester.runpytest(*backend_args)
    assert result.ret == 0


def test_strict_markers(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.no_xvfb
        def test_marked():
            pass
    """
    )
    result = pytester.runpytest("--strict")
    assert result.ret == 0


def test_xvfb_session_fixture(pytester: pytest.Pytester) -> None:
    """Make sure the xvfb fixture can be used from a session-wide one."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='session')
        def fixt(xvfb):
            pass

        def test_fixt(fixt):
            pass
    """
    )
    result = pytester.runpytest()
    assert result.ret == 0


@pytest.mark.skipif(not xauth_available, reason="no xauth")
def test_xvfb_with_xauth(pytester: pytest.Pytester, backend_args: list[str]) -> None:
    original_auth = os.environ.get("XAUTHORITY")
    pytester.makeini(
        """
        [pytest]
        xvfb_xauth = True
    """
    )
    pytester.makepyfile(
        """
        import os

        def test_xauth():
            print('\\nXAUTHORITY: ' + os.environ['XAUTHORITY'])
            assert os.path.isfile(os.environ['XAUTHORITY'])
            assert os.access(os.environ['XAUTHORITY'], os.R_OK)
    """
    )
    result = pytester.runpytest("-s", *backend_args)
    # Get and parse the XAUTHORITY: line
    authline = next(l for l in result.outlines if l.startswith("XAUTHORITY:"))
    authfile = authline.split(" ", 1)[1]

    assert result.ret == 0
    # Make sure the authfile is deleted
    assert not os.path.exists(authfile)
    assert os.environ.get("XAUTHORITY") == original_auth
