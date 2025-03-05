# imports
from pathlib import Path

import geopandas as gpd
import holoviews as hv
import hvplot.pandas
import pandas as pd
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
            ylabel="Population Percent (%)",
            title="Severe Housing Problems Across Total Population",
        ).opts(axiswise=True)

        return severe_housing_bar_chart

    @param.depends("places", "year", "demographic")
    def poverty_level_plot(self):
        place_name = self._get_place_name()
        columns_renamed = {
            f"us_pov_{self.demographic}_18": "US - Under 18",
            f"st_pov_{self.demographic}_18": "Nebraska - Under 18",
            f"pl_pov_{self.demographic}_18": f"{place_name} - Under 18",
            f"us_pov_{self.demographic}_tot": "US - Total Population",
            f"st_pov_{self.demographic}_tot": "Nebraska - Total Population",
            f"pl_pov_{self.demographic}_tot": f"{place_name} - Total Population",
        }

        # slim down data
        columns = self.base_columns + list(columns_renamed.keys())
        poverty_data = self._census[columns].rename(columns=columns_renamed)

        # filter data based on place and year
        poverty_data = poverty_data.loc[
            (poverty_data["PLACEFIPS"] == f"31{self.places}")
            & (poverty_data["year"] == str(self.year))
        ]

        poverty_bar_chart = poverty_data.hvplot.bar(
            ylabel="Population Percent (%)",
            title=f"Poverty Among {self.demographic} Demographic Group",
        ).opts(axiswise=True)

        return poverty_bar_chart

    def __panel__(self):
        return pn.Row(
            pn.Param(self, width=300, name="Filters"),
            pn.Column(
                pn.Row(
                    hv.DynamicMap(self.median_age_plot),
                    hv.DynamicMap(self.severe_housing_plot),
                ),
                hv.DynamicMap(self.poverty_level_plot),
            ),
        )


# return panel object with widgets and plot
