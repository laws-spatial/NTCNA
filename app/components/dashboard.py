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
    place = param.Selector(objects=PLACES_CODES)
    demographic = param.Selector(objects=DEMOGRAPHIC_CODES, default="total")
    year = param.Integer(default=2011, bounds=(2011, 2020))

    def __init__(self, **params):
        super().__init__(**params)
        self.base_columns: list = ["NAME", "PLACEFIPS", "year", "entityID"]
        self.plot_colors = ["#0b5394", "#666666", "#f1c232"]
        self.bar_chart_defaults = dict(axiswise=False, default_tools=["save"])

    def _get_place_name(self) -> str:
        return [key for key, val in PLACES_CODES.items() if val == self.place][0]

    def _get_demographic_name(self) -> str:
        return [
            key for key, val in DEMOGRAPHIC_CODES.items() if val == self.demographic
        ][0]

    def _create_title(self, demographic_name: str) -> str:
        match demographic_name:
            case "Total Population":
                return f"Poverty Among The {demographic_name}"
            case "Other":
                return f"Poverty Among Those Of {demographic_name} Descent"
            case "Two or More Races":
                return f"Poverty Among Those With {demographic_name}"
            case _:
                return f"Poverty Among {demographic_name}s"

    @param.depends("place", "year", "demographic")
    def median_age_plot(self) -> hv.Bars:
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
            (median_age_data["PLACEFIPS"] == f"31{self.place}")
            & (median_age_data["year"] == str(self.year))
        ]
        median_age_bar_chart = median_age_data.hvplot.bar(
            ylabel="Years",
            title="Median Age",
            color=self.plot_colors,
            ylim=(0, 75),
            # hover=False,
        ).opts(axiswise=True, toolbar=None)
        return median_age_bar_chart

    @param.depends("place", "year")
    def severe_housing_plot(self) -> hv.Bars:
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
            (severe_housing_data["PLACEFIPS"] == f"31{self.place}")
            & (severe_housing_data["year"] == str(self.year))
        ]

        # create bar chart
        severe_housing_bar_chart = severe_housing_data.hvplot.bar(
            ylabel="Population Percent (%)",
            title="Severe Housing Problems Across Total Population",
            color=self.plot_colors,
            ylim=(0, 35),
        ).opts(axiswise=False, toolbar=None)

        return severe_housing_bar_chart

    @param.depends("place", "year", "demographic")
    def poverty_level_plot(self) -> hv.Bars:
        place_name = self._get_place_name()

        # set up necessary column magic
        columns_renamed = {
            f"us_pov_{self.demographic}_18": "US",
            f"st_pov_{self.demographic}_18": "Nebraska",
            f"pl_pov_{self.demographic}_18": f"{place_name}",
            f"us_pov_{self.demographic}_tot": "US",
            f"st_pov_{self.demographic}_tot": "Nebraska",
            f"pl_pov_{self.demographic}_tot": f"{place_name}",
        }

        columns = self.base_columns + list(columns_renamed.keys())

        # read in data and rename columns
        poverty_data = self._census[columns].rename(columns=columns_renamed)

        # filter data based on place and year
        poverty_data = poverty_data.loc[
            (poverty_data["PLACEFIPS"] == f"31{self.place}")
            & (poverty_data["year"] == str(self.year))
        ]

        # morph data into usable format for graph
        realigned_poverty_data = (
            pd.melt(poverty_data, value_vars=list(columns_renamed.values()))
            .assign(  # this used for grouping in chart
                group=[
                    "Under 18",
                    "Total Population",
                    "Under 18",
                    "Total Population",
                    "Under 18",
                    "Total Population",
                ]
            )
            .set_index(["group", "variable"])  # set this multindex to graph propertly
        )

        # create title of graph
        demographic_name = self._get_demographic_name()
        title = self._create_title(demographic_name)

        # create chart
        poverty_bar_chart = realigned_poverty_data.hvplot.bar(
            ylabel="Population Percent (%)",
            title=title,
            color=self.plot_colors,
            ylim=(0, 100),
        ).opts(axiswise=False, toolbar=None, shared_axes=False)

        return poverty_bar_chart

    @param.depends("place", "year", "demographic")
    def population_by_age_group_plot(self):
        place_name = self._get_place_name()

        # set up necessary column magic
        columns_renamed = {
            f"us_age_{self.demographic}_und18": "US",
            f"st_age_{self.demographic}_und18": "Nebraska",
            f"pl_age_{self.demographic}_und18": f"{place_name}",
            f"us_age_{self.demographic}_18_64": "US",
            f"st_age_{self.demographic}_18_64": "Nebraska",
            f"pl_age_{self.demographic}_18_64": f"{place_name}",
            f"us_age_{self.demographic}_ov65": "US",
            f"st_age_{self.demographic}_ov65": "Nebraska",
            f"pl_age_{self.demographic}_ov65": f"{place_name}",
        }

        columns = self.base_columns + list(columns_renamed.keys())

        # read in data and rename columns
        age_group_data = self._census[columns]
        print(age_group_data)
        age_group_data = age_group_data.rename(columns=columns_renamed)

        # filter data based on place and year
        age_group_data = age_group_data.loc[
            (age_group_data["PLACEFIPS"] == f"31{self.place}")
            & (age_group_data["year"] == str(self.year))
        ]

        print(age_group_data)
        # morph data into usable format for graph
        realigned_age_group_data = (
            pd.melt(age_group_data, value_vars=list(columns_renamed.values()))
            .assign(  # this used for grouping in chart
                group=[
                    "Under 18 y.o.",
                    "18 to 64 y.o.",
                    "65 y.o. and older",
                    "Under 18 y.o",
                    "18 to 64 y.o.",
                    "65 y.o. and older",
                    "Under 18 y.o",
                    "18 to 64 y.o.",
                    "65 y.o. and older",
                ]
            )
            .set_index(["group", "variable"])  # set this multindex to graph propertly
        )
        print(realigned_age_group_data)
        # create chart
        age_group_bar_chart = realigned_age_group_data.hvplot.bar(
            ylabel="Population Percent (%)",
            title="Percentage of Population by Age Group",
            color=self.plot_colors,
            ylim=(0, 75),
        ).opts(axiswise=False, toolbar=None, shared_axes=False)

        return age_group_bar_chart

    # return panel object with widgets and plot
    def __panel__(self):
        return pn.Row(
            pn.Param(self, width=300, name="Filters"),
            pn.Column(
                pn.Row(
                    hv.DynamicMap(self.median_age_plot),
                    hv.DynamicMap(self.severe_housing_plot),
                ),
                pn.Row(
                    hv.DynamicMap(self.poverty_level_plot),
                    hv.DynamicMap(self.population_by_age_group_plot),
                ),
            ),
        )
