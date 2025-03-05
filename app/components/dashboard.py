# imports
from pathlib import Path

import geopandas as gpd

# import panel as pn
import param
from config import DEMOGRAPHIC_CODES, PLACES_CODES

# ### read in data
data_path = Path("data")

# # census data
census_data_path = data_path / "ne_ntcna_places_census.geojson"
census_data = gpd.read_file(census_data_path)

# # chas data
chas_data_path = data_path / "ne_ntcna_places_chas.geojson"
chas_data = gpd.read_file(chas_data_path)


# subclass param.Parameterized in Dashboard class
class NTCNA_Dashboard(param.Parameterized):
    """
    Dashboard for NTCNA data
    """

    # define widgets from params
    _census = param.DataFrame(census_data, precedence=-1)
    _chas = param.DataFrame(chas_data, precedence=-1)
    places = param.Selector(objects=PLACES_CODES)
    demographic = param.Selector(objects=DEMOGRAPHIC_CODES, default="total")
    year = param.Integer(default=2011,  bounds=(2011, 2020))

    def __init__(self, **params):
        super().__init__(**params)

    def median_age_plot(self):

        data = 

    # def __panel__(self):
    #     return pn.Column(self.places)


# return panel object with widgets and plot
#     def view(self):
