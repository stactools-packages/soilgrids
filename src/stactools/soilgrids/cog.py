import logging
import os
import shutil
from subprocess import CalledProcessError, check_output
from tempfile import TemporaryDirectory
from typing import List

import rasterio

from stactools.soilgrids.constants import (
    DEPTHS,
    PROBS,
    SOIL_PROPERTIES,
    TILING_PIXEL_SIZE,
)

logger = logging.getLogger(__name__)


def process_dataset(
        source: str,
        output_directory: str,
        properties: List(str) = SOIL_PROPERTIES.keys(),
) -> None:
    for prop in properties:
        for depth in DEPTHS.keys():
            for prob in PROBS.keys():
                with TemporaryDirectory() as tmp_dir:
                    file_name = f"{prop}/{prop}_{depth}_{prob}.vrt"
                    create_tiled_cogs(os.path.join(source, file_name), tmp_dir)
                    item_path = os.path.join(
                        output_directory,
                        f"{prop}_{depth}_{prob}",
                    )
                    os.makedirs(item_path, exist_ok=True)
                    logger.info(f"Moving assets to {item_path}")
                    for file in os.listdir(tmp_dir):
                        file_path = os.path.join(tmp_dir, file)
                        with rasterio.open(file_path, "r") as dataset:
                            if dataset.read().any():
                                destination = os.path.join(
                                    item_path,
                                    file.replace(".vrt", ".tif"),
                                )
                                shutil.move(file_path, destination)


def create_tiled_cogs(
    input_file: str,
    output_directory: str,
) -> None:
    """Split tiff into tiles and create COGs

    Args:
        input_path (str): Path to the soilgrids VRT file.
        output_directory (str): The directory to which the COGs will be written.

    Returns:
        None
    """
    logger.info(f"Retiling {input_file}")
    cmd = [
        "gdal_retile.py",
        "-ps",
        str(TILING_PIXEL_SIZE[0]),
        str(TILING_PIXEL_SIZE[1]),
        "-of",
        "COG",
        "-co",
        "NUM_THREADS=ALL_CPUS",
        "-co",
        "BLOCKSIZE=512",
        "-co",
        "COMPRESS=DEFLATE",
        "-co",
        "LEVEL=9",
        "-co",
        "PREDICTOR=YES",
        "-co",
        "OVERVIEWS=IGNORE_EXISTING",
        "-targetDir",
        output_directory,
        input_file,
    ]
    try:
        output = check_output(cmd)
    except CalledProcessError as e:
        output = e.output
        raise
    finally:
        logger.info(f"output: {str(output)}")


def create_cog(
    input_path: str,
    output_path: str,
    raise_on_fail: bool = True,
    dry_run: bool = False,
) -> str:
    """Create COG from a tif

    Args:
        input_path (str): Path to the Natural Resources Canada Land Cover data.
        output_path (str): The path to which the COG will be written.
        raise_on_fail (bool, optional): Whether to raise error on failure.
            Defaults to True.
        dry_run (bool, optional): Run without downloading tif, creating COG,
            and writing COG. Defaults to False.

    Returns:
        str: The path to the output COG.
    """

    output = None
    try:
        if dry_run:
            logger.info(
                "Would have downloaded TIF, created COG, and written COG")
        else:
            cmd = [
                "gdal_translate",
                "-of",
                "COG",
                "-co",
                "BLOCKSIZE=512",
                "-co",
                "compress=deflate",
                "-co",
                "predictor=yes",
                "-co",
                "OVERVIEWS=IGNORE_EXISTING",
                input_path,
                output_path,
            ]

            try:
                output = check_output(cmd)
            except CalledProcessError as e:
                output = e.output
                raise
            finally:
                logger.info(f"output: {str(output)}")

    except Exception:
        logger.error("Failed to process {}".format(output_path))

        if raise_on_fail:
            raise

    return output_path
