# imports
from pathlib import Path

import geopandas as gpd
import param

### read in data
data_path = Path("data")

# census data
census_data_path = data_path / "ne_ntcna_places_census.geojson"
census_data = gpd.read_file(census_data_path)

# chas data
chas_data_path = data_path / "ne_ntcna_places_chas.geojson"
chas_data = gpd.read_file(chas_data_path)


# subclass param.Parameterized in Dashboard class
class NTCNA_Dashboard(param.Parameterized):
    """
    Dashboard for NTCNA data
    """

    # define widgets from params
    _census = param.DataFrame(census_data, precedence=0)
    _chas = param.DataFrame(chas_data, precedence=0)


# setup sidebar of widgets

# create median age plot

# return panel object with widgets and plot
