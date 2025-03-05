# imports
from pathlib import Path

import geopandas as gpd
from param import Parameterized

### read in data
data_path = Path("data")

# census data
census_data_path = data_path / "ne_ntcna_places_census_viz.geojson"
census_data = gpd.read_file(census_data_path)

# chas data
chas_data_path = data_path / "ne_ntcna_places_chas_viz.geojson"
chas_data = gpd.read_file(chas_data_path)


# subclass param.Parameterized in Dashboard class
class NTCNA_Dashboard(Parameterized):
    """
    Dashboard for NTCNA data
    """


# define widgets from params

# setup sidebar of widgets

# create median age plot

# return panel object with widgets and plot
