# -*- coding: utf-8 -*-

"""Make sure things don't break on Windows with no Xvfb available."""


def test_xvfb_windows(testdir):
    testdir.makepyfile("""
        def test_nothing():
            pass
    """)
    result = testdir.runpytest()
    assert result.ret == 0
