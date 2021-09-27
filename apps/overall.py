#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
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



##comment this line if just running on own ##############################################################################
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


JourneysDF.tail(5)
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

JourneysFinalDF.tail(5)


# In[ ]:


GroupedDayOutDF= pd.DataFrame(JourneysFinalDF.groupby(['dayout'])['bikeid'].count()).reset_index()
GroupedDayOutDF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)
daycode={'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5,'Saturday':6,'Sunday':7}
GroupedDayOutDF['DayCode']=GroupedDayOutDF['dayout'].map(daycode)
GroupedDayOutDF=GroupedDayOutDF.sort_values(by=['DayCode'],ascending=True)
print(GroupedDayOutDF)


# In[ ]:


out_df = JourneysFinalDF[['stationout','stationoutid','dateout']]
out_df['BikesOut'] = 1
out_df['BikesIn'] = 0
out_df['BikesMovements'] = 1
out_df.rename(columns={'stationout':'Stationname','stationoutid':'StationID'},inplace=True)
# print(out_df)

return_df = JourneysFinalDF[['stationin','stationinid','dateout']]
return_df['BikesOut'] = 0
return_df['BikesIn'] = 1
return_df['BikesMovements'] = 1
return_df.rename(columns={'stationin':'Stationname','stationinid':'StationID'},inplace=True)
# print(return_df)

station_df = pd.concat([out_df,return_df],ignore_index=True)
# print(station_df)


#Stations = pd.read_csv('Stations.csv')
mergeddf = pd.merge(station_df, StationsDF, 
                     left_on = 'StationID', 
                     right_on = 'stationid', 
                     how='left')

# print(mergeddf)


newdf = pd.DataFrame(mergeddf.groupby(['stationname','longitude','latitude'])['BikesOut','BikesIn','BikesMovements'].sum()).reset_index()



newdf['ratio'] = (newdf['BikesOut']/ newdf['BikesMovements'])*100



newdf['size'] = (newdf['BikesMovements'].apply(lambda x: (np.sqrt(x/100) + 1) if x > 500 else (np.log(x) / 2 + 1)).replace(np.NINF, 0))*3

print(newdf)


# In[ ]:


fig1 = go.Figure(data=[go.Bar(
            x=GroupedDayOutDF.dayout.unique(), y=GroupedDayOutDF['NumberPickUps'],
            text=GroupedDayOutDF['NumberPickUps'],
            textposition='auto',
            
        )])

fig1.update_layout(title={
        'text': "Bike Hires by Day of the Week",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
                   xaxis_title='Day of the Week',
                   yaxis_title='Number of Hires')


# In[ ]:


GroupedHourOutDF= pd.DataFrame(JourneysFinalDF.groupby(['hourout'])['bikeid'].count()).reset_index()
GroupedHourOutDF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)

fig2 = go.Figure(data=[go.Bar(
            x=GroupedHourOutDF.hourout.unique(), y=GroupedHourOutDF['NumberPickUps'],
            text=GroupedHourOutDF['NumberPickUps'],
            textposition='auto',
            
        )])

fig2.update_layout(title={
        'text': "Bike Hires by Hour of the Day",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
                   xaxis_title='Day of the Week',
                   yaxis_title='Number of Hires')


# In[ ]:


GroupedDateOutDF= pd.DataFrame(JourneysFinalDF.groupby(['dateout'])['bikeid'].count()).reset_index()
GroupedDateOutDF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)



fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=GroupedDateOutDF['dateout'], y=GroupedDateOutDF['NumberPickUps'],
                    mode='lines',
                    name='Bikes Going Out'))

fig3.update_layout(
    title={
        'text': "Bike Hires over Time",
        'y':0.85,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis_title="Date",
    yaxis_title="Number of Bikes Hired")


# In[ ]:


external_stylesheets = [
    {
        "rel": "stylesheet",
    },
]


# In[ ]:


# mask = (
#          (merged_df.Startstation == "17th St & Penn Ave")
        
#     )

# filtered_data = merged_df.loc[mask, :]

# print(filtered_data)


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
            dbc.Button("Station Data", color="primary", className="mr-1", href='/apps/stations'), 
            dbc.Button("Forecast Use", color="primary", className="mr-1", href='/apps/forecast'),
            ]
        ),
            
        ],style={'text-align':'center'}
    ),
]


# In[ ]:


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) ########################################
# server = app.server        ##################################################################################

# app.title = "Pittsburgh Healthy Ride Bikes Network Analysis!" ###########################################################################


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
    
 
        

   ###########################################################################################################################
    
     dbc.Row([
         
         dbc.Col([
         
         dcc.Graph(id='fig1', figure=fig1),
         
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
         ),
     ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}
       
     ),

   ###########################################################################################################################
    
     dbc.Row([
         
         dbc.Col([
         
         dcc.Graph(id='fig2', figure=fig2),
         
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
         ),
     ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}
       
     ),

    ###########################################################################################################################
    
     dbc.Row([
         
         dbc.Col([
         
         dcc.Graph(id='fig3', figure=fig3),
         
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
         ),
     ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}
       
     ),
 

    
], fluid=True)

#############################################################################################################################
if __name__ == "__main__":
    app.run_server(debug=True)


# In[ ]:




