from pathlib import Path

import colorcet as cc
import geopandas as gpd
import panel as pn
import param
from config import DEMOGRAPHIC_CODES, PLACES_CODES
from lonboard import Map, PolygonLayer

pn.extension("ipywidgets")

# ### read in data
data_path = Path("./data")


@pn.cache
def load_data(path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(path)


# # census data
census_data_path = data_path / "ne_ntcna_places_census.geojson"
census_data = load_data(census_data_path)

# # chas data
chas_data_path = data_path / "ne_ntcna_places_chas.geojson"
chas_data = load_data(chas_data_path)


year_options = sorted(year for year in census_data["year"].unique() if year)


class MapView(pn.viewable.Viewer):
    """Map view for visualizing census and CHAS data."""

    value = param.ClassSelector(
        class_=Map, doc="Map for visualizing data", constant=True, precedence=-1
    )
    place = param.Selector(objects=PLACES_CODES)
    # demographic = param.Selector(objects=DEMOGRAPHIC_CODES, default="total")
    year = param.Integer(default=2011, bounds=(2011, 2020))
    zoom = param.Integer(default=12, bounds=(1, 20))

    data = param.DataFrame(precedence=-1)

    def __init__(self, **params):
        self.longitude = -97.21714077402164
        self.latitude = 42.35875453986342

        params["value"] = params.get(
            "value",
            Map(
                layers=[],
                view_state={
                    "longitude": self.longitude,
                    "latitude": self.latitude,
                    "zoom": self.zoom,
                },
            ),
        )

        super().__init__(**params)

        self.value.layout.height = self.value.layout.width = "100%"

        self.settings = pn.Column(
            # pn.widgets.Select.from_param(
            #     self.param.demographic, sizing_mode="stretch_width", name="Demographic"
            # ),
            pn.widgets.Select.from_param(
                self.param.place, sizing_mode="stretch_width", name="Place"
            ),
            pn.widgets.IntSlider.from_param(
                self.param.year, sizing_mode="stretch_width", name="Year"
            ),
            pn.widgets.IntSlider.from_param(
                self.param.zoom, sizing_mode="stretch_width", name="Zoom"
            ),
            margin=5,
            sizing_mode="fixed",
            width=300,
        )

        self.view = pn.Column(
            self._title, pn.pane.IPyWidget(self.value, sizing_mode="stretch_both")
        )
        self._layout = pn.Row(
            pn.Column(self.settings, sizing_mode="fixed", width=300),
            self.view,
            sizing_mode="stretch_both",
        )

    @param.depends("year", "place", watch=True, on_init=True)
    def _update_data(self):
        data = census_data.loc[
            (census_data["year"] == f"{self.year}")
            & (census_data["entityID"] == f"{self.place}")
        ]
        self.latitude = data["geometry"].centroid.y.values[0]
        self.longitude = data["geometry"].centroid.x.values[0]
        self.data = data

    @param.depends("data", "zoom", watch=True)
    def _update_value(self):
        layer = PolygonLayer.from_geopandas(self.data)
        layer.get_color = [200, 40, 40]
        self.value.layers = [layer]
        self.value.view_state = {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "zoom": self.zoom,
        }

    @param.depends("year", "place", watch=True)
    def _title(self):
        return f"# Statistics for {self.year}"

    # def __panel__(self):
    #     return pn.Row(
    #         pn.Param(self, width=150, name="Filters"),
    #         pn.pane.IPyWidget(self.value, height=1000, width=500),
    #     )

    def __panel__(self):
        return self._layout
