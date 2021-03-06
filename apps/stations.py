#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
#import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go

import pandas as pd
import numpy as np
#import pathlib



##comment this line if just running on own ###############################################################################
from app import app


import mysql.connector
from mysql.connector import Error
from datetime import datetime
from pytz import timezone

localhost = 'pittsburghdb.c9rczggk5uzn.eu-west-2.rds.amazonaws.com'
username = 'pittsburghadmin'
password = 'Pitts$8burgh'
databasename='pittsburgh'
port=3306



database_connection = mysql.connector.connect(host=localhost, database=databasename, 
user=username, password=password)

JourneysDF = pd.read_sql('SELECT * FROM journeys', con=database_connection)
StationsDF = pd.read_sql('SELECT * FROM stations', con=database_connection)
BikesOutDF = pd.read_sql('SELECT * FROM bikesout', con=database_connection)
BikesLocationsDF = pd.read_sql('SELECT * FROM bikeslocations', con=database_connection)




# In[ ]:


timeZone='America/New_York'

#Set Local Time

now=datetime.now()
nowLocal = now.astimezone(timezone(timeZone))
localDateTime = datetime.strptime(nowLocal.strftime('%Y-%m-%d'), '%Y-%m-%d')


#Format for visualisatioh
nowLocalWords=nowLocal.strftime("%A %d %B %Y")
timeHHMM = nowLocal.strftime("%H:%M")


# In[ ]:


JourneysDF
#JourneyDF = pd.merge(Journeys,StationsDF[['StationName','StationID']],on='StationName', how='left')


# In[ ]:


StationsDF.head(5)


# In[ ]:


JourneysDF = JourneysDF.merge(StationsDF[['stationid','stationname','latitude','longitude']],
                                              left_on=['stationoutid'],right_on=['stationid'],how='left')
JourneysDF.drop('stationid', inplace=True, axis=1)

JourneysDF.head(5)


# In[ ]:


JourneysDF=JourneysDF.rename(columns={'stationname': 'stationout','latitude': 'latout','longitude': 'longout'})

#stationout, latout, longout


# In[ ]:


JourneysDF = JourneysDF.merge(StationsDF[['stationid','stationname','latitude','longitude']],
                                              left_on=['stationinid'],right_on=['stationid'],how='left')
JourneysDF.drop('stationid', inplace=True, axis=1)
JourneysDF.head(5)


# In[ ]:


JourneysDF=JourneysDF.rename(columns={'stationname': 'stationin','latitude': 'latin','longitude': 'longin'})
JourneysDF.head(5)


# In[ ]:


JourneysFinalDF = JourneysDF


# In[ ]:


JourneysFinalDF['dateout'] = [d.date() for d in JourneysFinalDF['datetimeout']]
JourneysFinalDF['dateout'] = pd.to_datetime(JourneysFinalDF['dateout'],format='%Y-%m-%d')
JourneysFinalDF['datein'] = [d.date() for d in JourneysFinalDF['datetimein']]
JourneysFinalDF['datein'] = pd.to_datetime(JourneysFinalDF['datein'],format='%Y-%m-%d')

JourneysFinalDF['timeout'] = JourneysFinalDF['datetimeout'].dt.strftime('%H:%M:%S')
JourneysFinalDF['timein'] = JourneysFinalDF['datetimein'].dt.strftime('%H:%M:%S')


JourneysFinalDF.dtypes


# In[ ]:


JourneysFinalDF['dayout']=JourneysFinalDF['dateout'].dt.day_name()
JourneysFinalDF['dayin']=JourneysFinalDF['datein'].dt.day_name()
JourneysFinalDF['hourout']=pd.to_datetime(JourneysFinalDF['timeout']).dt.hour
JourneysFinalDF['hourin']=pd.to_datetime(JourneysFinalDF['timein']).dt.hour

JourneysFinalDF['journeytime']=((JourneysFinalDF['datetimein']-JourneysFinalDF['datetimeout']).dt.total_seconds()/60)
JourneysFinalDF['journeytime']=JourneysFinalDF['journeytime'].astype(int)

JourneysFinalDF= JourneysFinalDF[(JourneysFinalDF['journeytime'] >= 3)]
JourneysFinalDF.reset_index(drop=True, inplace=True)

JourneysFinalDF


# In[ ]:


GroupedDF= pd.DataFrame(JourneysFinalDF.groupby(['stationout','dateout'])['bikeid'].count()).reset_index()
GroupedDF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)


# In[ ]:


GroupedDF


# In[ ]:


Grouped2DF= pd.DataFrame(JourneysFinalDF.groupby(['stationout','dateout','hourout'])['bikeid'].count()).reset_index()
Grouped2DF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)
Grouped2DF.isna().sum()


# In[ ]:


external_stylesheets = [
    {
        "rel": "stylesheet",
    },
]


# In[ ]:


mask = (
         (GroupedDF.stationout == "Hobart St & Wightman St")
        
    )

filtered_data = GroupedDF.loc[mask, :]

print(filtered_data)


# In[ ]:


mask2 = (
         (Grouped2DF.stationout == "Hobart St & Wightman St")
        
    )

filtered_data2 = Grouped2DF.loc[mask2, :]

print(filtered_data2)


# In[ ]:


menu_content = [
    dbc.CardHeader("Pittsburgh Healthy Ride Bike Scheme",style={'text-align':'center'}),
    dbc.CardBody(
        [
            html.H3("Current Network Status",className="card-title"),
            html.H4("Figures correct to local time of", className="card-title"),
            html.H4(f"{timeHHMM}"),
            html.H4(f"{nowLocalWords}"),
            html.H4(" "),
            html.H5("Please select to view other data"),
            html.Div([
            dbc.Button("Today's Data", color="primary", className="mr-1", href='/apps/gettoday'),
            dbc.Button("Historic Data", color="primary", className="mr-1", href='/apps/overall'),  
            dbc.Button("Forecast Use", color="primary", className="mr-1", href='/apps/forecast'),
            ]
        ),
            
        ],style={'text-align':'center'}
    ),
]


# In[ ]:





# In[ ]:


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) ########################################
# server = app.server        ##################################################################################

# app.title = "Pittsburgh Healthy Ride Bikes Network Analysis!" ########################################################


## Header

layout = dbc.Container([
  
     dbc.Row([
    
        dbc.Col([
            dbc.Card([
                    dbc.CardImg(
                        src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Healthy_Ride.png",
                        bottom=True),
                ],
                 #style={"width": "100%", "height": "100px", "display": "block"},  
                style={"width": "100%"},
            )
        ], width={'size':3},
          
        ),


        dbc.Col([
            dbc.Card(menu_content, color="warning", inverse=True, style={'height':'90%'})
            
            
        ], style={"height": "100%"}
            
            ),
        
        
        
        dbc.Col([
            dbc.Card([
                    dbc.CardImg(
                        src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Healthy_Ride.png",
                        bottom=True),
                ],
                 #style={"width": "100%", "height": "100px", "display": "block"},  
                style={"width": "100%"},
            )
        ], width={'size':3},
          
        ),
        
    ], style={"height": "350px"}
           
    ),
    
  ####################################################################################################################  
    
    
    
    
          dbc.Row([
        
## MENUS        
        
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Select station to look at", className="menu-title"),
                        dcc.Dropdown(
                            id="station-filter",
                            options=[
                                {"label": stationout, "value": stationout}
                                for stationout in np.sort(GroupedDF.stationout.unique())
                            ],
                            value="Hobart St & Wightman St",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),


                 html.Div(
                    children=[
                        html.Div(
                            children="Select data range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=JourneysFinalDF.dateout.min().date(),
                            max_date_allowed=JourneysFinalDF.dateout.max().date(),
                            start_date=JourneysFinalDF.dateout.min().date(),
                            end_date=JourneysFinalDF.dateout.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),

        
          ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 
                     'padding-top': '70px'}
          ),
              
        
## GRAPHS 
    
    dbc.Row([
    
        
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="BelfastJourneyPickups", config={"displayModeBar": False},
                        
                    ),
                    className="card",
                ),



            ],
            className="wrapper",
        ),
        
      ],   
   ),

###############################################################################################################
    
      dbc.Row([
    
        
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="PickUpsByHourOfDay", config={"displayModeBar": False},
                        
                    ),
                    className="card",
                ),



            ],
            className="wrapper",
        ),
        
      ],   
   )
    
    
    
    


], fluid=True)


###############################################################################################################
@app.callback(
    
    Output("BelfastJourneyPickups", "figure"),  ##add other in here
    
    [
        Input("station-filter", "value"),        
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(stationout, start_date, end_date):
    mask = (
         (GroupedDF.stationout == stationout)
       & (GroupedDF.dateout >= start_date)
       & (GroupedDF.dateout <= end_date)
    )
    filtered_data = GroupedDF.loc[mask, :]
    
    
    fig = px.line(filtered_data, x=filtered_data["dateout"], y=filtered_data["NumberPickUps"], 
                  
                title="Number of station pick ups per day",
                    #  title_x=0.5,  
                  labels=dict(NumberPickUps="Total Bikes Picked Up From Station",dateout="Date of Rental"))

    return fig

#######################################################################################################
@app.callback(
    
    Output("PickUpsByHourOfDay", "figure"),  ##add other in here
    
    [
        Input("station-filter", "value"),        
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(stationout, start_date, end_date):
    mask2 = (
         (Grouped2DF.stationout == stationout)
       & (Grouped2DF.dateout >= start_date)
       & (Grouped2DF.dateout <= end_date)
    )
    filtered_data2 = Grouped2DF.loc[mask2, :]
    
    
    #fig2 = go.Figure([go.Bar(x=filtered_data2["hourout"], y=filtered_data2["NumberPickUps"])])
    fig2 = px.bar(filtered_data2, x='hourout', y='NumberPickUps')
    fig2.update_layout(title={
        'text': "Number of pick ups from the station by hour of the day",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
                   xaxis_title='Hour of Day',
                   yaxis_title='Number of Hires')

    return fig2

#######################################################################################################

if __name__ == "__main__":
    app.run_server(debug=True)##############################################################################


# In[ ]:




