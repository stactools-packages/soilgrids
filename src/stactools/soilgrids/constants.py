# flake8: noqa

from pystac import Link, Provider, ProviderRole

SOILGRIDS_ID = "SoilGrids"
SOILGRIDS_EPSG = 152160
SOILGRIDS_CRS_WKT = """PROJCS["Homolosine",
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
SOILGRIDS_TITLE = "ISRIC SoilGrids Global Soil Property Maps"
LICENSE = "CC-BY-4.0"
LICENSE_LINK = Link(
    rel="license",
    target="https://creativecommons.org/licenses/by/4.0/",
    title="Creative Commons Attribution 4.0 International"
)

DATASET_URL = "https://files.isric.org/soilgrids/latest/data/"
DATASET_ACCESS_URL = f"/vsicurl?max_retry=3&retry_delay=1&list_dir=no&url={DATASET_URL}"

SOILGRIDS_DESCRIPTION = """SoilGridsTM (hereafter SoilGrids) is a system for global digital soil mapping that makes use of global soil profile information and covariate data to model the spatial distribution of soil properties across the globe. SoilGrids is a collections of soil property maps for the world produced using machine learning at 250 m resolution."""

SOILGRIDS_PROVIDER = Provider(
    name="ISRIC — World Soil Information",
    roles=[
        ProviderRole.HOST,
        ProviderRole.PROCESSOR,
        ProviderRole.PRODUCER,
    ],
    url=
    "https://www.isric.org/explore/soilgrids")

SOILGRIDS_BOUNDING_BOX = [96.00, -44.00, 168.00, -9.00]
SOILGRIDS_START_YEAR = "2021"
SOILGRIDS_END_YEAR = "2021"

DOI = "10.5194/soil-7-217-2021"
CITATION = "Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., and Rossiter, D.: SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty, SOIL, 7, 217–240, 2021."

#pH, soil organic carbon content, bulk density, coarse fragments content, sand content, silt content, clay content, cation exchange capacity (CEC), total nitrogen as well as soil organic carbon density and soil organic carbon stock

SOIL_PROPERTIES = {
    "bdod": "Bulk density of the fine earth fraction (cg/cm³)",
    # "cec": "Cation Exchange Capacity of the soil (mmol(c)/kg)",
    # "cfvo": "",
    # "clay": "",
    # "nitrogen": "",
    # "ocd": "",
    # "ocs": "",  # only 0-30cm
    # "phh2o": "",
    # "sand": "",
    # "silt": "",
    # "soc": "",
}
DEPTHS = {
    "0-5cm": "Zero to 5cm Depth",
    # "5-15cm": "5cm to 15cm Depth",
    # "15-30cm": "15cm to 30cm Depth",
    # "30-60cm": "30cm to 60cm Depth",
    # "60-100cm": "60cm to 100cm Depth",
    # "100-200cm": "100cm to 200cm Depth",
}
PROBS = {
    "Q0.05": "",
    # "Q0.5": "",
    # "Q0.95": "",
    # "mean": "",
    # "uncertainty": "",
}

TILING_PIXEL_SIZE = (10000, 10000)
