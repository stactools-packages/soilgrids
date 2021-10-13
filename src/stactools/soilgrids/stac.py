import logging
from datetime import datetime, timezone

from pystac import (Asset, CatalogType, Collection, Extent, Item, ItemCollection, MediaType,
                    Provider, ProviderRole, SpatialExtent, TemporalExtent)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
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
                                           DOI, CITATION, SOILGRIDS_CRS_WKT, TILE_GEOS,
                                           SOILGRIDS_DEPTHS, SOILGRIDS_PROB, SOILGRIDS_TYPES)

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
        tile_props={
            "title": r"ISRIC Soilgrids Tile ID",
            "href": f"https://www.isric.org/explore/soilgrid/tiles/{tile_id}.json",
        }
        tile_item=Item(
            id=tile_id,
            geometry=tile_goes,
            bbox=tile_goes["coordinates"],
            datetime=start_time,
            properties=tile_props)
        for soil_type, soil_desc in SOILGRIDS_TYPES.items():
            for depth, depth_desc in SOILGRIDS_DEPTHS.items():
                for prob, prob_desc in SOILGRIDS_PROB.items():
                    tile_item.add_asset(f"extent-{tile_id}-{depth}-{prob}", Asset(
                        href="https://www.isric.org/explore/soilgrid/tiles/{tile_id}-{depth}-{prob}.COG",
                        media_type=MediaType.COG,
                        roles=["extent"],
                        title=f"ISRIC Soilgrids {soil_desc}-{depth_desc}-{prob}: tile {tile_id}",
                    ))
        print(tile_item)
        items.append(tile_item)
    col_items = ItemCollection(items=items)
    collection.add_items(col_items)

    return collection

def create_item(asset_href: str) -> Item:
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
        id = os.path.basename(asset_href).replace("_cog", "").replace(".tif", "")
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
