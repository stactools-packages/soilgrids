import logging
import os
import re
from typing import Optional

import fsspec
import rasterio
from pyproj import CRS, Proj
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.file import FileExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from pystac.extensions.scientific import ScientificExtension
from shapely.geometry import box, mapping
from stactools.core.io import ReadHrefModifier

from stactools.soilgrids.constants import (
    BOUNDING_BOX,
    CITATION,
    COLLECTION_ID,
    CRS_WKT,
    DEPTHS,
    DESCRIPTION,
    DOI,
    EPSG,
    LICENSE,
    LICENSE_LINK,
    NO_DATA,
    PROBS,
    PROVIDER,
    RELEASE_DATE,
    SCALES,
    SOIL_PROPERTIES,
    TITLE,
    UNITS,
)

logger = logging.getLogger(__name__)


def create_collection() -> Collection:
    """Create a STAC Collection using

    This function includes logic to extract all relevant metadata from
    an asset describing the STAC collection and/or metadata coded into an
    accompanying constants.py file.

    See `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_.

    Returns:
        Collection: STAC Collection object
    """
    extent = Extent(
        SpatialExtent([BOUNDING_BOX]),
        TemporalExtent([RELEASE_DATE, None]),
    )

    collection = Collection(
        id=COLLECTION_ID,
        title=TITLE,
        description=DESCRIPTION,
        license=LICENSE,
        providers=[PROVIDER],
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    collection.add_link(LICENSE_LINK)
    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [EPSG]

    collection_sci = ScientificExtension.ext(collection, add_if_missing=True)
    collection_sci.doi = DOI
    collection_sci.citation = CITATION

    return collection


def wrap_href(href: str, href_modifier: Optional[ReadHrefModifier]) -> str:
    if href_modifier:
        return href_modifier(href)
    return href


def create_item(
    asset_dir_href: str,
    asset_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Create a STAC Item a given ISRIC Soilgrids TILE ID, DEPTH and PROB tuple or filename.

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to a directory containing the items's assets

    Returns:
        Item: STAC Item object
    """
    item_id = os.path.basename(asset_dir_href.rstrip("/"))
    match = re.match(r"(.*)_(.*)_(\d\d)_(\d\d)", item_id)
    if match is None:
        raise ValueError(
            f"Couldn't extract item identifiers from {asset_dir_href}")
    prop, depth, tile1, tile2 = match.groups()
    if prop not in SOIL_PROPERTIES:
        raise ValueError(f"'{prop}' is not a recognized soil property")
    if depth not in DEPTHS:
        raise ValueError(f"'{depth}' is not a recognized depth")

    item = None
    for prob in PROBS:
        asset_href = os.path.join(
            asset_dir_href,
            f"{prop}_{depth}_{prob}_{tile1}_{tile2}.tif",
        )
        asset_access_href = wrap_href(asset_href, asset_href_modifier)
        logger.debug(f"Opening asset at: {asset_href}")
        logger.debug(f"With access href: {asset_access_href}")
        with rasterio.open(asset_access_href) as dataset:
            bbox = list(dataset.bounds)
            geometry = mapping(box(*bbox))
            transform = dataset.transform
            shape = dataset.shape

        if item is None:
            # Create item
            # This only gets executed once
            logger.debug(f"Creating item {item_id}")
            transformer = Proj.from_crs(
                CRS.from_wkt(CRS_WKT),
                CRS.from_epsg(4326),
                always_xy=True,
            )
            bbox_4326 = list(
                transformer.transform_bounds(
                    dataset.bounds.left,
                    dataset.bounds.bottom,
                    dataset.bounds.right,
                    dataset.bounds.top,
                ))
            geometry_4326 = mapping(box(*bbox_4326, ccw=True))
            properties = {
                "title": "title",
                "description": "description",
            }
            item = Item(
                id=item_id,
                geometry=geometry_4326,
                bbox=bbox_4326,
                datetime=RELEASE_DATE,
                properties=properties,
                stac_extensions=[],
            )

            item_proj_ext = ProjectionExtension.ext(item, add_if_missing=True)
            item_proj_ext.epsg = EPSG
            item_proj_ext.wkt2 = CRS_WKT
            item_proj_ext.bbox = bbox
            item_proj_ext.geometry = geometry
            item_proj_ext.shape = shape
            item_proj_ext.transform = transform

            item_sci_ext = ScientificExtension.ext(item, add_if_missing=True)
            item_sci_ext.doi = DOI
            item_sci_ext.citation = CITATION

        asset = Asset(
            href=asset_href,
            media_type=MediaType.COG,
            roles=["data"],
            title="A dummy STAC Item COG",
        )
        item.add_asset(
            prob,
            asset,
        )
        # File Extension
        asset_file_ext = FileExtension.ext(asset, add_if_missing=True)
        with fsspec.open(asset_access_href) as file:
            size = file.size
            if size is not None:
                asset_file_ext.size = size
        # Raster Extension
        asset_raster_ext = RasterExtension.ext(asset, add_if_missing=True)
        band = RasterBand.create(
            nodata=NO_DATA,
            sampling=Sampling.AREA,
            data_type=DataType.UINT8,
            spatial_resolution=30,
            unit=UNITS[prop],
        )
        if prop in SCALES:
            band.scale = SCALES[prop]
        asset_raster_ext.bands = [band]
        # Projection Extension
        asset_proj_ext = ProjectionExtension.ext(asset, add_if_missing=True)
        asset_proj_ext.epsg = item_proj_ext.epsg
        asset_proj_ext.wkt2 = item_proj_ext.wkt2
        asset_proj_ext.bbox = item_proj_ext.bbox
        asset_proj_ext.geometry = item_proj_ext.geometry
        asset_proj_ext.transform = item_proj_ext.transform
        asset_proj_ext.shape = item_proj_ext.shape
    assert item
    return item
