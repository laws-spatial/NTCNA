# imports
from pathlib import Path

import geopandas as gpd
import holoviews as hv
import hvplot.pandas

# import panel as pn
import param
from config import DEMOGRAPHIC_CODES, PLACES_CODES

# import hvplot.pandas


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
    year = param.Integer(default=2011, bounds=(2011, 2020))

    @param.depends("places", "year", "demographic")
    def median_age_plot(self):
        # set up for renaming columns to be more human readable
        places_column_name = [
            key for key, val in PLACES_CODES.items() if val == self.places
        ][0]

        columns_renamed = {
            f"pl_medage_{self.demographic}": places_column_name,
            f"st_medage_{self.demographic}": "State",
            f"us_medage_{self.demographic}": "US",
        }

        # slim down data
        base_columns = ["NAME", "PLACEFIPS", "year", "entityID"]
        columns = base_columns + list(columns_renamed.keys())
        data = self._census[columns].rename(columns=columns_renamed)

        # filter data based on place and year
        data = data.loc[
            (self._census["PLACEFIPS"] == f"31{self.places}")
            & (self._census["year"] == str(self.year))
        ]

        # create bar chart
        bars = data.hvplot.bar(xlabel="Geography", ylabel="Years", title="Median Age")

        return bars


# return panel object with widgets and plot
