import logging
from datetime import datetime, timezone

from pystac import (Asset, CatalogType, Collection, Extent, Item, ItemCollection, MediaType,
                    Provider, ProviderRole, SpatialExtent, TemporalExtent)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from pystac.extensions.scientific import ScientificExtension
from stactools.soilgrids.constants import (SOILGRIDS_ID, SOILGRIDS_EPSG, SOILGRIDS_TITLE,
                                           SOILGRIDS_DESCRIPTION, SOILGRIDS_PROVIDER, LICENSE,
                                           LICENSE_LINK, SOILGRIDS_BOUNDING_BOX,
                                           SOILGRIDS_START_YEAR, SOILGRIDS_END_YEAR,
                                           DOI, CITATION, SOILGRIDS_CRS_WKT, TILE_GEOS, SOILGRIDS_TYPES)

logger = logging.getLogger(__name__)


def create_collection() -> Collection:
    """Create a STAC Collection

    This function includes logic to extract all relevant metadata from
    an asset describing the STAC collection and/or metadata coded into an
    accompanying constants.py file.

    See `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_.

    Returns:
        Collection: STAC Collection object
    """
    providers = [SOILGRIDS_PROVIDER]

    # Time must be in UTC
    start_time = datetime.strptime(SOILGRIDS_START_YEAR, '%Y')

    extent = Extent(
        SpatialExtent([SOILGRIDS_BOUNDING_BOX]),
        TemporalExtent([start_time, None]),
    )

    collection = Collection(
        id=SOILGRIDS_ID,
        title=SOILGRIDS_TITLE,
        description=SOILGRIDS_DESCRIPTION,
        license=LICENSE,
        providers=providers,
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    collection.add_link(LICENSE_LINK)
    collection_proj = ProjectionExtension.summaries(collection, add_if_missing=True)
    collection_proj.epsg = [SOILGRIDS_EPSG]
    collection_proj.wkt2 = SOILGRIDS_CRS_WKT

    collection_sci = ScientificExtension.ext(collection, add_if_missing=True)
    collection_sci.doi = DOI
    collection_sci.citation = CITATION

    items=[]
    for tile_id, tile_goes in TILE_GEOS.items():
        tile_props={}
        tile_item=Item(collection=collection, id=tile_id, geometry=tile_goes, bbox=tile_goes["coordinates"], datetime=start_time, properties=tile_props)
        items.append(tile_item)
    collection_items = ItemCollection(items=items)

    return collection


def create_item(asset_href: str) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """

    properties = {
        "title": "A dummy STAC Item",
        "description": "Used for demonstration purposes",
    }

    demo_geom = {
        "type":
        "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90],
                         [-180, -90]]],
    }

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    item = Item(
        id="my-item-id",
        properties=properties,
        geometry=demo_geom,
        bbox=[-180, 90, 180, -90],
        datetime=demo_time,
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

    return item
