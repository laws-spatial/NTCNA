from pathlib import Path

import colorcet as cc
import geopandas as gpd
import panel as pn
import param
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
    year = param.Selector(
        default=year_options[0], objects=year_options, doc="Year to visualize"
    )
    # cmap: str = param.Selector(
    #     default=cc.fire, objects=cc.palette, label="cmap by Colorcet"
    # )

    data = param.DataFrame(precedence=-1)

    def __init__(self, **params):
        params["value"] = params.get(
            "value",
            Map(
                layers=[],
                view_state={
                    "longitude": -97.21714077402164,
                    "latitude": 42.35875453986342,
                    "zoom": 7,
                },
            ),
        )

        super().__init__(**params)

        # self.value.layout.height = self.value.layout.width = "100%"

    @param.depends("year", watch=True, on_init=True)
    def _update_data(self):
        self.data = census_data[census_data["year"] == self.year]

    @param.depends("data", watch=True)
    def _update_value(self):
        layer = PolygonLayer.from_geopandas(self.data)
        layer.get_color = [200, 40, 40]
        self.value.layers = [layer]

    def __panel__(self):
        return pn.Row(
            pn.Param(self, width=150, name="Filters"),
            pn.pane.IPyWidget(self.value, height=1000, width=500),
        )
