import panel as pn
from components.dashboard import NTCNA_Dashboard

ntcna_dashboard = NTCNA_Dashboard()

pn.panel(ntcna_dashboard.param).servable()
