# flake8: noqa

from datetime import datetime

from pystac import Link, Provider, ProviderRole

COLLECTION_ID = "SoilGrids"
EPSG = 152160
CRS_WKT = """PROJCS["Homolosine",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
   AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    PROJECTION["Interrupted_Goode_Homolosine"],
    UNIT["Meter",1]]"""
TITLE = "ISRIC SoilGrids Global Soil Property Maps"
LICENSE = "CC-BY-4.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://creativecommons.org/licenses/by/4.0/",
    title="Creative Commons Attribution 4.0 International",
)

DATASET_URL = "https://files.isric.org/soilgrids/latest/data/"
DATASET_ACCESS_URL = f"/vsicurl?max_retry=3&retry_delay=1&list_dir=no&url={DATASET_URL}"

DESCRIPTION = """SoilGridsTM (hereafter SoilGrids) is a system for global digital soil mapping that makes use of global soil profile information and covariate data to model the spatial distribution of soil properties across the globe. SoilGrids is a collections of soil property maps for the world produced using machine learning at 250 m resolution."""

PROVIDER = Provider(
    name="ISRIC — World Soil Information",
    roles=[
        ProviderRole.HOST,
        ProviderRole.PROCESSOR,
        ProviderRole.PRODUCER,
    ],
    url="https://www.isric.org/explore/soilgrids",
)

BOUNDING_BOX = [96.00, -44.00, 168.00, -9.00]
RELEASE_DATE = datetime(2020, 5, 1)

DOI = "10.5194/soil-7-217-2021"
CITATION = "Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., and Rossiter, D.: SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty, SOIL, 7, 217–240, 2021."

SOIL_PROPERTIES = {
    "bdod": "Bulk density of the fine earth fraction (cg/cm³)",
    "cec": "Cation Exchange Capacity of the soil (mmol(c)/kg)",
    "cfvo":
    "Volumetric fraction of coarse fragments (> 2 mm) (cm3/dm3 (vol‰))",
    "clay":
    "Proportion of clay particles (< 0.002 mm) in the fine earth fraction (g/kg)",
    "nitrogen": "Total nitrogen (cg/kg)",
    "ocd": "Organic carbon density (hg/m³)",
    "ocs": "Organic carbon stocks (t/ha)",  # only 0-30cm
    "phh2o": "Soil pH (pHx10)",
    "sand":
    "Proportion of sand particles (> 0.05 mm) in the fine earth fraction (g/kg)",
    "silt":
    "Proportion of silt particles (≥ 0.002 mm and ≤ 0.05 mm) in the fine earth fraction (g/kg)",
    "soc": "Soil organic carbon content in the fine earth fraction (dg/kg)",
}
DEPTHS = {
    "0-5cm": "Zero to 5cm Depth",
    "5-15cm": "5cm to 15cm Depth",
    "15-30cm": "15cm to 30cm Depth",
    "30-60cm": "30cm to 60cm Depth",
    "60-100cm": "60cm to 100cm Depth",
    "100-200cm": "100cm to 200cm Depth",
}
PROBS = {
    "Q0.05": "5% quantile",
    "Q0.5": "median of the distribution",
    "Q0.95": "95% quantile",
    "mean": "mean of the distribution",
    "uncertainty": "10x(Q0.95-Q0.05)/Q0.50",
}

TILING_PIXEL_SIZE = (10000, 10000)
