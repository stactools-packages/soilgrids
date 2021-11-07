import logging
import os
from datetime import datetime
from typing import Optional

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
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from pystac.extensions.scientific import ScientificExtension
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
    PROBS,
    PROVIDER,
    RELEASE_DATE,
    SOIL_PROPERTIES,
    TITLE,
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


def create_item(
    asset_href: str,
    asset_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Create a STAC Item a given ISRIC Soilgrids TILE ID, DEPTH and PROB tuple or filename.

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """

    asset_href_relative = None
    if asset_href and not uri_validator(asset_href):
        asset_href_relative = os.path.relpath(asset_href, destination)
    if extent_asset_href and not uri_validator(extent_asset_href):
        extent_asset_href = os.path.relpath(extent_asset_href, destination)
    cog_access_href = asset_href  # Make sure cog_access_href exists, even if None
    if asset_href and asset_href_modifier:
        cog_access_href = asset_href_modifier(asset_href)

    title = metadata["tiff_metadata"]["dct:title"]
    description = metadata["description_metadata"]["dct:description"]

    utc = pytz.utc

    year = title.split(" ")[0]
    dataset_datetime = utc.localize(datetime.strptime(year, "%Y"))

    end_datetime = dataset_datetime + relativedelta(years=5)

    start_datetime = dataset_datetime
    end_datetime = end_datetime

    if asset_href is not None:
        id = os.path.basename(asset_href).replace("_cog",
                                                  "").replace(".tif", "")
    else:
        id = title.replace(" ", "-")
    cog_geom = get_cog_geom(cog_access_href, metadata)
    bbox = cog_geom["bbox"]
    geometry = cog_geom["geometry"]
    tiled = cog_geom["tiled"]

    properties = {
        "title": title,
        "description": description,
    }

    # Create item
    item = pystac.Item(
        id=id,
        geometry=geometry,
        bbox=bbox,
        datetime=dataset_datetime,
        properties=properties,
        stac_extensions=[],
    )

    # It is a good idea to include proj attributes to optimize for libs like stac-vrt
    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    proj_attrs.epsg = 4326
    proj_attrs.bbox = [-180, 90, 180, -90]
    proj_attrs.shape = [1, 1]  # Raster shape
    proj_attrs.transform = [-180, 360, 0, 90, 0, 180]  # Raster GeoTransform

    # Add an asset to the item (COG for example)
    item.add_asset(
        "image",
        Asset(
            href=asset_href,
            media_type=MediaType.COG,
            roles=["data"],
            title="A dummy STAC Item COG",
        ),
    )
    if start_datetime and end_datetime:
        item.common_metadata.start_datetime = start_datetime
        item.common_metadata.end_datetime = end_datetime

    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = SOILGRIDS_EPSG
    item_projection.wkt2 = SOILGRIDS_CRS_WKT
    if cog_href is not None:
        item_projection.bbox = cog_geom["cog_bbox"]
        item_projection.transform = cog_geom["transform"]
        item_projection.shape = cog_geom["shape"]

    return item
