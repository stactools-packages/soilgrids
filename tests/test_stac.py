import os
import unittest

from stactools.soilgrids import stac
from tests import test_data


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        collection = stac.create_collection()
        collection.set_self_href("")

        # TODO: Stub test, test at least the existence of basic fields and STAC Extensions
        self.assertEqual(collection.id, "soilgrids250m")

        collection.validate()

    def test_create_item(self):
        test_path = test_data.get_path("data-files/cogs")
        for asset_dir in filter(os.path.isdir, os.listdir(test_path)):
            item = stac.create_item(asset_dir)

            # TODO: Stub test, test at least the existence of basic fields and STAC Extensions

            item.validate()
