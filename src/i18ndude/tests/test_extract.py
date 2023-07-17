"""Tests for the message string extraction tool.
"""

from doctest import DocTestSuite

import unittest


def test_suite():
    return unittest.TestSuite((DocTestSuite("i18ndude.extract"),))


if __name__ == "__main__":
    unittest.main()
