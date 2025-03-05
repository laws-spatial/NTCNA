# imports
from pathlib import Path

import geopandas as gpd
import holoviews as hv
import hvplot.pandas
import panel as pn
import param
from config import DEMOGRAPHIC_CODES, PLACES_CODES
from panel.viewable import Viewer

# ### read in data
data_path = Path("data")

# # census data
census_data_path = data_path / "ne_ntcna_places_census.geojson"
census_data = gpd.read_file(census_data_path)

# # chas data
chas_data_path = data_path / "ne_ntcna_places_chas.geojson"
chas_data = gpd.read_file(chas_data_path)


# subclass param.Parameterized in Dashboard class
# class NTCNA_Dashboard(param.Parameterized):
class NTCNA_Dashboard(Viewer):
    """
    Dashboard for NTCNA data
    """

    # define widgets from params
    _census = param.DataFrame(census_data, precedence=-1)
    _chas = param.DataFrame(chas_data, precedence=-1)
    places = param.Selector(objects=PLACES_CODES)

    demographic = param.Selector(objects=DEMOGRAPHIC_CODES, default="total")
    year = param.Integer(default=2011, bounds=(2011, 2020))

    def __init__(self, **params):
        super().__init__(**params)
        self.base_columns: list = ["NAME", "PLACEFIPS", "year", "entityID"]

    def _get_place_name(self):
        return [key for key, val in PLACES_CODES.items() if val == self.places][0]

    @param.depends("places", "year", "demographic")
    def median_age_plot(self):
        # set up for renaming columns to be more human readable
        place_name = self._get_place_name()
        columns_renamed = {
            f"us_medage_{self.demographic}": "US",
            f"st_medage_{self.demographic}": "Nebraska",
            f"pl_medage_{self.demographic}": place_name,
        }

        # slim down data
        columns = self.base_columns + list(columns_renamed.keys())
        median_age_data = self._census[columns].rename(columns=columns_renamed)

        # filter data based on place and year
        median_age_data = median_age_data.loc[
            (median_age_data["PLACEFIPS"] == f"31{self.places}")
            & (median_age_data["year"] == str(self.year))
        ]
        median_age_bar_chart = median_age_data.hvplot.bar(
            ylabel="Years",
            title="Median Age",
        ).opts(axiswise=True)

        return median_age_bar_chart

    @param.depends("places", "year")
    def severe_housing_plot(self):
        # set up for renaming columns to be more human readable
        place_name = self._get_place_name()
        columns_renamed = {
            "us_sev_housing": "US",
            "st_sev_housing": "Nebraska",
            "pl_sev_housing": place_name,
        }

        # slim down data
        columns = self.base_columns + list(columns_renamed.keys())
        severe_housing_data = self._chas[columns].rename(columns=columns_renamed)

        severe_housing_data = severe_housing_data.loc[
            (severe_housing_data["PLACEFIPS"] == f"31{self.places}")
            & (severe_housing_data["year"] == str(self.year))
        ]

        # create bar chart
        severe_housing_bar_chart = severe_housing_data.hvplot.bar(
            ylabel="Percentage of Population",
            title="Severe Housing Population (%)",
        ).opts(axiswise=True)

        return severe_housing_bar_chart

    def __panel__(self):
        return pn.Row(
            pn.Param(self, width=300, name="Filters"),
            self.median_age_plot,
            self.severe_housing_plot,
        )


# return panel object with widgets and plot
