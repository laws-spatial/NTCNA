import panel as pn
from components.dashboard import NTCNA_Dashboard

ntcna_dashboard = NTCNA_Dashboard()

pn.panel(
    pn.Row(
        ntcna_dashboard.param,
        ntcna_dashboard.median_age_plot,
    )
).servable()
