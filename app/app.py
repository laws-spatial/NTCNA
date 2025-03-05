# import panel as pn
from components.dashboard import NTCNA_Dashboard

ntcna_dashboard = NTCNA_Dashboard()

ntcna_dashboard.servable()
# pn.panel(
#     pn.Row(
#         ntcna_dashboard.param,
#         ntcna_dashboard.median_age_plot,
#         ntcna_dashboard.severe_housing_plot,
#         # pn.Column(ntcna_dashboard.median_age_plot, ntcna_dashboard.severe_housing_plot),
#     )
# ).servable()
