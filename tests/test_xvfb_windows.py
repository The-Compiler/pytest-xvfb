"""Make sure things don't break on Windows with no Xvfb available."""


def test_xvfb_windows(pytester):
    pytester.makepyfile(
        """
        def test_nothing():
            pass
    """
    )
    result = pytester.runpytest()
    assert result.ret == 0
