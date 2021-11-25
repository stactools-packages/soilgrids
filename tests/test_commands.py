import os.path
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.soilgrids.commands import create_soilgrids_command
from tests import test_data


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_soilgrids_command]

    # TODO: Stub test. It only ensures completion of the command
    def test_create_collection(self):
        with TemporaryDirectory() as tmp_dir:
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(
                ["soilgrids", "create-collection", destination])

            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(destination)
            self.assertEqual(collection.id, "soilgrids250m")

            collection.validate()

    # TODO: Stub test. It only ensures completion of the command
    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            test_path = test_data.get_path("data-files/cogs")
            for asset_dir in filter(os.path.isdir, os.listdir(test_path)):
                destination = os.path.join(tmp_dir, "collection.json")
                result = self.run_command([
                    "soilgrids",
                    "create-item",
                    os.path.join(test_path, asset_dir),
                    destination,
                ])
                self.assertEqual(result.exit_code,
                                 0,
                                 msg="\n{}".format(result.output))

                jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
                self.assertEqual(len(jsons), 1)

                item = pystac.read_file(destination)
                self.assertEqual(item.id, "soilgrids250m")

                item.validate()
