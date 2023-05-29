from __future__ import annotations

import os
import sys

import pytest


if sys.version_info == (3, 12, 0, "beta", 1) and "CI" in os.environ:
    pytest.skip(
        reason="Segfaults on GHA for unknown reasons",
        allow_module_level=True,
    )

pytest.importorskip("PyQt5.QtWebEngineWidgets")


def test_qt_output(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
    import sys
    import PyQt5.QtWebEngineWidgets
    from PyQt5.QtWidgets import QWidget, QApplication

    app = QApplication(sys.argv)

    def test_widget():
        widget = QWidget()
        widget.show()
    """
    )
    res = pytester.runpytest()
    assert res.ret == 0
