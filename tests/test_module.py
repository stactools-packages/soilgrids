import unittest

import stactools.soilgrids


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.soilgrids.__version__)
