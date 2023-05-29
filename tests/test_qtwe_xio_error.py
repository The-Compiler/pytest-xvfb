from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("PyQt5.QtWebEngineWidgets")


@pytest.mark.skipif(
    sys.version_info == (3, 12, 0, "beta", 1) and "CI" in os.environ,
    reason="Segfaults on GHA for unknown reasons",
)
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
