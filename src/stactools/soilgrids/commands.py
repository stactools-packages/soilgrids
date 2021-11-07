import logging
import os
from typing import List

import click
from soilgrids.src.stactools.soilgrids.constants import SOIL_PROPERTIES

from stactools.soilgrids import cog, stac
from stactools.soilgrids.constants import DATASET_ACCESS_URL

logger = logging.getLogger(__name__)


def create_soilgrids_command(cli):
    """Creates the stactools-soilgrids command line utility."""
    @cli.group(
        "soilgrids",
        short_help=("Commands for working with stactools-soilgrids"),
    )
    def soilgrids():
        pass

    @soilgrids.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

    @soilgrids.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

    @soilgrids.command(
        "cogify",
        short_help="Download data files, tile, and convert to COG",
    )
    @click.option(
        "-s",
        "--source",
        required=False,
        help="URL or path to dataset",
        default=DATASET_ACCESS_URL,
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json",
    )
    @click.option(
        "-p",
        "--property",
        multiple=True,
        required=False,
        help="Property to process, can be passed multiple times",
        default=SOIL_PROPERTIES.keys(),
    )
    def cogify(source: str, destination: str, property: List[str]) -> None:
        """Creates a STAC Collection and all of its Items and Assets
        Args:
            destination (str): Path for the STAC Collection
            source (str, optional): URL or path to dataset
            property (str, multiple): Property to process, can be passed multiple times
        """
        for p in property:
            if p not in SOIL_PROPERTIES.keys():
                raise ValueError("Not a valid soil property: {p}")
        cog.process_dataset(source, destination, property)

    @soilgrids.command(
        "create-full-collection",
        short_help="Get all data files and create Items and Collection",
    )
    @click.option(
        "-s",
        "--source",
        required=False,
        help="URL or path to dataset",
        default=DATASET_ACCESS_URL,
    )
    @click.option(
        "-d",
        "--destination",
        required=True,
        help="The output directory for the STAC json",
    )
    def create_full_collection(source: str, destination: str) -> None:
        """Creates a STAC Collection and all of its Items and Assets
        Args:
            destination (str): Path for the STAC Collection
        """
        os.chdir(destination)
        # collection = stac.create_monthly_collection()
        # collection.normalize_hrefs("./")
        # collection.save(dest_href="./")
        cog.process_dataset(source, "./")
        # for file_name in glob("./*tmin*.tif"):
        #     logger.info(f"Processing {file_name}")
        #     id = stac.create_monthly_item(file_name).id
        #     os.makedirs(id, exist_ok=True)
        #     for data_var in MONTHLY_DATA_VARIABLES.keys():
        #         var_file_name = file_name.replace("tmin", data_var)
        #         shutil.move(var_file_name, os.path.join(id, var_file_name))
        #     item = stac.create_monthly_item(os.path.join(id, file_name))
        #     collection.add_item(item)
        #     item.validate()
        # logger.info("Saving collection")
        # collection.normalize_hrefs("./")
        # collection.make_all_asset_hrefs_relative()
        # collection.save(dest_href="./")
        # collection.validate()

    return soilgrids
