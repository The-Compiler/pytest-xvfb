import pytest

pytest.importorskip("PyQt5.QtWebEngineWidgets")

def test_qt_output(pytester):
    pytester.makepyfile("""
    import sys
    import PyQt5.QtWebEngineWidgets
    from PyQt5.QtWidgets import QWidget, QApplication

    app = QApplication(sys.argv)

    def test_widget():
        widget = QWidget()
        widget.show()
    """)
    res = pytester.runpytest()
    assert res.ret == 0
