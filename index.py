#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import gettoday, overall, stations, forecast
# from apps import forecast


app.layout = html.Div([
    html.Div([
#         dcc.Link('Todays Data |', href='/apps/gettoday'),
#         dcc.Link('Historic Data |', href='/apps/overall'),
#         dcc.Link('Historic Stations Data |', href='/apps/stations'),
#         dcc.Link('5 Day Forecast |', href='/apps/forecast'),
#         dcc.Link('Testing |', href='/apps/testing'),
#     ], className="row"),
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content', children=[])
])




# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'path')])
# def display_page(path):
# #     if path == '/apps/gettoday':
# #         return gettoday.layout
# #     if path == '/apps/overall':
# #         return overall.layout
# #     if path == '/apps/stations':
# #         return stations.layout
# #     if path == '/apps/forecast':
# #         return forecast.layout
#     if path == '/apps/forecast':
#         return testing.layout
#     else:
#         return testing.layout


if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:





# In[ ]:




