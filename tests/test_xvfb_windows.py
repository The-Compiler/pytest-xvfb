from __future__ import annotations

import pytest


def test_xvfb_windows(pytester: pytest.Pytester) -> None:
    """Make sure things don't break on Windows with no Xvfb available."""
    pytester.makepyfile(
        """
        def test_nothing():
            pass
    """
    )
    result = pytester.runpytest()
    assert result.ret == 0
