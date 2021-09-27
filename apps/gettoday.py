#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Import Python Packages
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_table.Format import Format, Sign

import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go

import pandas as pd
import numpy as np
#import pathlib

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from pytz import timezone

from app import app ###############################################################################################

timeZone='America/New_York'


# In[2]:


# Connect to database and read in data to DataFrames

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


# In[3]:


print(JourneysDF['datetimein'].max())


BikesGroupedDF = BikesLocationsDF.groupby(['stationid'])['bikeid'].count().reset_index(name="countbikes")
BikesGroupedDF

StationBikesDF = StationsDF.merge(BikesGroupedDF,on=['stationid'],how='left')
StationBikesDF['countbikes']=StationBikesDF['countbikes'].fillna(0)
StationBikesDF['countbikes']=StationBikesDF['countbikes'].astype(int)
StationBikesDF['availablespaces']=StationBikesDF['racksize']-StationBikesDF['countbikes']
StationBikesDF=StationBikesDF[(StationBikesDF['countbikes']<3) | (StationBikesDF['availablespaces']<3)]
StationBikesDF


# In[4]:


#Set Local Time

now=datetime.now()
nowLocal = now.astimezone(timezone(timeZone))
localDateTime = datetime.strptime(nowLocal.strftime('%Y-%m-%d'), '%Y-%m-%d')


#Format for visualisatioh
nowLocalWords=nowLocal.strftime("%A %d %B %Y")
timeHHMM = nowLocal.strftime("%H:%M")

Tomorrow = localDateTime + timedelta(days=1)

timeLocalHourAgo =nowLocal+ timedelta(hours=-1)
timeLocalHourAgo= timeLocalHourAgo.replace(tzinfo=None)


# In[5]:


BikesInStationsData = len(BikesLocationsDF.index)
BikesOutData = len(BikesOutDF.index)


# In[6]:


JourneysDF = JourneysDF[(JourneysDF['datetimeout'])>localDateTime]
JourneysDF = JourneysDF[(JourneysDF['datetimein'])<Tomorrow]

JourneysTodayData = len(JourneysDF)


# In[7]:


JourneysHourData = len(JourneysDF[(JourneysDF['datetimein'])>timeLocalHourAgo])


# In[8]:


StationsDF.head(5)


# In[9]:


#Merge station dataframe to journeys dataframe so to add station name and latitude longitude data (First for Station Bike out
#taken out from)
JourneysDF = JourneysDF.merge(StationsDF[['stationid','stationname','latitude','longitude']],
                                              left_on=['stationoutid'],right_on=['stationid'],how='left')
JourneysDF.drop('stationid', inplace=True, axis=1)

JourneysDF.head(5)


# In[ ]:





# In[10]:


#R
JourneysDF=JourneysDF.rename(columns={'stationname': 'stationout','latitude': 'latout','longitude': 'longout'})

#stationout, latout, longout


# In[11]:


#Then merge again to get the same data for the station bike returned to
JourneysDF = JourneysDF.merge(StationsDF[['stationid','stationname','latitude','longitude']],
                                              left_on=['stationinid'],right_on=['stationid'],how='left')
JourneysDF.drop('stationid', inplace=True, axis=1)
JourneysDF.head(5)


# In[12]:


JourneysDF=JourneysDF.rename(columns={'stationname': 'stationin','latitude': 'latin','longitude': 'longin'})
JourneysDF.head(5)


# In[13]:


JourneysFinalDF = JourneysDF


# In[14]:


#Split DateTime fields to date and time to make easier to work with
JourneysFinalDF['dateout'] = [d.date() for d in JourneysFinalDF['datetimeout']]
JourneysFinalDF['dateout'] = pd.to_datetime(JourneysFinalDF['dateout'],format='%Y-%m-%d')
JourneysFinalDF['datein'] = [d.date() for d in JourneysFinalDF['datetimein']]
JourneysFinalDF['datein'] = pd.to_datetime(JourneysFinalDF['datein'],format='%Y-%m-%d')

JourneysFinalDF['timeout'] = JourneysFinalDF['datetimeout'].dt.strftime('%H:%M:%S')
JourneysFinalDF['timein'] = JourneysFinalDF['datetimein'].dt.strftime('%H:%M:%S')


JourneysFinalDF.dtypes


# In[15]:


#Further split date time fields to columns of days of week and hours of day for graphing purposes
JourneysFinalDF['dayout']=JourneysFinalDF['dateout'].dt.day_name()
JourneysFinalDF['dayin']=JourneysFinalDF['datein'].dt.day_name()
JourneysFinalDF['hourout']=pd.to_datetime(JourneysFinalDF['timeout']).dt.hour
JourneysFinalDF['hourin']=pd.to_datetime(JourneysFinalDF['timein']).dt.hour

JourneysFinalDF['journeytime']=((JourneysFinalDF['datetimein']-JourneysFinalDF['datetimeout']).dt.total_seconds()/60)
JourneysFinalDF['journeytime']=JourneysFinalDF['journeytime'].astype(int)

JourneysFinalDF= JourneysFinalDF[(JourneysFinalDF['journeytime'] >= 5)]
JourneysFinalDF= JourneysFinalDF[(JourneysFinalDF['datetimeout'] > '2020-12-31')]
JourneysFinalDF.reset_index(drop=True, inplace=True)

JourneysFinalDF


# In[16]:


#Create GroupedOutDF to show data for days of the week 

GroupedDayOutDF= pd.DataFrame(JourneysFinalDF.groupby(['dayout'])['bikeid'].count()).reset_index()
GroupedDayOutDF.rename(columns={'bikeid':'NumberPickUps'},inplace=True)
daycode={'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5,'Saturday':6,'Sunday':7}
GroupedDayOutDF['DayCode']=GroupedDayOutDF['dayout'].map(daycode)
GroupedDayOutDF=GroupedDayOutDF.sort_values(by=['DayCode'],ascending=True)
print(GroupedDayOutDF)


# In[17]:


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




newdf = pd.DataFrame(mergeddf.groupby(['stationname','longitude','latitude'])['BikesOut','BikesIn','BikesMovements'].sum()).reset_index()



newdf['ratio'] = (newdf['BikesOut']/ newdf['BikesMovements'])*100



newdf['size'] = (newdf['BikesMovements'].apply(lambda x: (np.sqrt(x/100) + 1) if x > 50 else (np.log(x) / 2 + 1)).replace(np.NINF, 0))*3

print(newdf)


# In[18]:


fig1 = go.Figure(data=[go.Bar(
            x=GroupedDayOutDF.dayout.unique(), y=GroupedDayOutDF['NumberPickUps'],
            text=GroupedDayOutDF['NumberPickUps'],
            textposition='auto',
            
        )])

fig1.update_layout(
    title='Bike Hires By Day of the Week')


# In[19]:


fig2 = go.Figure(
    go.Scattermapbox(
        lat=newdf['latitude'],
        lon=newdf['longitude'],
        mode='markers',
        
        marker=go.scattermapbox.Marker(

            size=(newdf['BikesMovements']),
#            color=newdf['ratio'],
 #           showscale=True,
          #  colorbar={'title':'% movements<br>' 
          #            'that are<br>'
          #            'journey<br>'
          #            'starts', 'titleside':'top', 'thickness':10}
        ),
        customdata=np.stack((pd.Series(newdf['stationname']), newdf['BikesOut'], newdf['BikesIn'],newdf['BikesMovements']), axis=-1),
        hovertemplate= """<extra></extra>
      <em>%{customdata[0]}  </em><br>
  ➡️  %{customdata[1]} Bikes Taken<br>
  ⬅️  %{customdata[2]} Bikes Returned<br>
  ↔️ %{customdata[3]} Bike Movements""",
    )
)


# Specify layout information
fig2.update_layout(
    font_family="Arial",
    font_color="blue",
    font_size=12,
    height=500,
    width=1000,
    margin = dict(l = 0, r = 0, t = 0, b = 0),
    
    title=dict(
        text='<b>Bike pick ups and returns</b>',
        x=0.5,
        y=0.85,
        font=dict(
            family="Arial",
            size=20,
            color='#000000'
        )),
    mapbox=dict(
        accesstoken='pk.eyJ1Ijoibmlja21hcHMiLCJhIjoiY2t0YWV4amJ2MDE4NTJvbGp5bm1xaHR6aCJ9.6GRCStGG-bw5vZPjkXsZKA', 
        center=go.layout.mapbox.Center(lat=40.44, lon=-79.98),
        zoom=11.5
    )
)


# In[20]:


completeOutDF=pd.DataFrame(columns=[])
completeOutDF['datetimeout']=JourneysFinalDF['datetimeout']
completeOutDF.sort_values(by=['datetimeout'],inplace=True)
#completeOutDF.drop('Count',axis=1,inplace=True)
completeOutDF['Count']= range(1, 1+len(completeOutDF))
completeOutDF['Count2'] = np.arange(completeOutDF.shape[0])

completeInDF=pd.DataFrame(columns=[])
completeInDF['datetimein']=JourneysFinalDF['datetimein']
completeInDF.sort_values(by=['datetimein'],inplace=True)
completeInDF['Count']= range(1, 1+len(completeInDF))


figLine = go.Figure()
figLine.add_trace(go.Scatter(x=completeOutDF['datetimeout'], y=completeOutDF['Count'],
                    mode='lines',
                    name='Bikes Going Out'))
figLine.add_trace(go.Scatter(x=completeInDF['datetimein'],y=completeInDF['Count'],
                    mode='lines',
                    name='Bikes Returning'))
figLine.update_layout(
    title={
        'text': "Bike Movements Over Today",
        'y':0.85,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis_title="Time of Day",
    yaxis_title="Number of Bikes")


# In[21]:


external_stylesheets = [
    {
        "rel": "stylesheet",
    },
]


# In[22]:


# mask = (
#          (merged_df.Startstation == "17th St & Penn Ave")
        
#     )

# filtered_data = merged_df.loc[mask, :]

# print(filtered_data)


# In[23]:


# app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #########################################################
# server = app.server

# app.title = "Belfast Bike Network Analysis!"


# ## Header

# app.layout = html.Div( #######################################################################################################
#     children=[
#         html.Div(
#             children=[
#                 html.P(children="🚴", className="header-emoji"),
#                 html.H1(
#                     children="Belfast", className="header-title"
#                 ),
#                 html.P(
#                     children="Bike Network Analysis - 2020",
                
#                     className="header-description",
#                 ),
#             ],
#             className="header",
#         ),
        

        
# ## MENUS        
        
# #         html.Div(
# #             children=[
# #                 html.Div(
# #                     children=[
# #                         html.Div(children="Select station to look at", className="menu-title"),
# #                         dcc.Dropdown(
# #                             id="station-filter",
# #                             options=[
# #                                 {"label": Startstation, "value": Startstation}
# #                                 for Startstation in np.sort(merged_df.Startstation.unique())
# #                             ],
# #                             value="17th St & Penn Ave",
# #                             clearable=False,
# #                             className="dropdown",
# #                         ),
# #                     ]
# #                 ),


# #                  html.Div(
# #                     children=[
# #                         html.Div(
# #                             children="Select data range", className="menu-title"
# #                         ),
# #                         dcc.DatePickerRange(
# #                             id="date-range",
# #                             min_date_allowed=merged_df.Startdate.min().date(),
# #                             max_date_allowed=merged_df.Startdate.max().date(),
# #                             start_date=merged_df.Startdate.min().date(),
# #                             end_date=merged_df.Startdate.max().date(),
# #                         ),
# #                     ]
# #                 ),
# #             ],
# #             className="menu",
# #      ),

        
        
# ## GRAPHS        
        
#         html.Div(
#             children=[
#                 html.Div(
#                     children=dcc.Graph(
#                         id="PittsJourneys", config={"displayModeBar": False},
#                         figure=fig1
                        
#                     ),
#                     className="card",
#                 ),


#                 html.Div(
#                     children=dcc.Graph(id='example-graph-2',
#                                        figure=fig2
#                     ),
#                     className="card",
#                 ),
                
#             ],
#             className="wrapper",
#         ),
        
#     ]
# )


# # @app.callback(
# #     Output("PittsJourneys", "figure"),    ##add other in here
# #     [
# #         Input("station-filter", "value"),        
# #         Input("date-range", "start_date"),
# #         Input("date-range", "end_date"),
# #     ],
# # )

# # def update_charts(Startstation, start_date, end_date):
# #     mask = (
# #          (merged_df.Startstation == Startstation)
# #        & (merged_df.Startdate >= start_date)
# #        & (merged_df.Startdate <= end_date)
# #     )
# #     filtered_data = merged_df.loc[mask, :]
    
    
# #     fig = px.line(filtered_data, x=filtered_data["Startdate"], y=filtered_data["NumberUps"], 
                  
# #                 title="Number of station pick ups per day",
# #                     #  title_x=0.5,  
# #                   labels=dict(NumberUps="Total Bikes Picked Up From Station",Startdate="Date of Rental"))

# #     return fig


# if __name__ == "__main__": ####################################################################################################
#     app.run_server(debug=False)################################################################################################


# In[24]:


# Workings for 


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
            dbc.Button("Historic Data", color="primary", className="mr-1", href='/apps/overall'),
            dbc.Button("Station Data", color="primary", className="mr-1", href='/apps/stations'),
            dbc.Button("Forecast Use", color="primary", className="mr-1", href='/apps/forecast'),
            ]
        ),
            
        ],style={'text-align':'center'}
    ),
]



card_content1 = [
    dbc.CardHeader("BIKE JOURNEYS",style={'text-align':'center'}),
    dbc.CardBody(
        [
            html.H5("Number of bike journeys today", className="card-title"),
            html.H3(f"{JourneysTodayData}",
                className="card-text",
            ),
        ],style={'text-align':'center'}
    ),
]

card_content2 = [
    dbc.CardHeader("BIKE JOURNEYS",style={'text-align':'center'}),
    dbc.CardBody(
        [
            html.H5("Number of bike journeys in the last hour", className="card-title"),
            html.H3(f"{JourneysHourData}",
                className="card-text",
            ),
        ],style={'text-align':'center'}
    ),
]

card_content3 = [
    dbc.CardHeader("BIKE IN STATIONS",style={'text-align':'center'}),
    dbc.CardBody(
        [
            html.H5("Number of bikes available in all stations", className="card-title"),
            html.H3(f"{BikesInStationsData}",
                className="card-text",
            ),
        ],style={'text-align':'center'}
    ),
]

card_content4 = [
    dbc.CardHeader("BIKES ON ROAD",style={'text-align':'center'}),
    dbc.CardBody(
        [
            html.H5("Number of bikes currently on the road", className="card-title"),
            html.H3(f"{BikesOutData}",
                className="card-text",
            ),
        ],style={'text-align':'center'}
    ),
]


# In[25]:


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) #########################################################
# server = app.server ##########################################################################################################

# app.title = "Pittsburgh Healthy Bike Network Analysis!" ######################################################################





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
    
##########################################################################################################################    
    
    dbc.Row(
            [
                dbc.Col(dbc.Card(card_content1, color="success", inverse=True)),
                dbc.Col(dbc.Card(card_content2, color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content3, color="danger", inverse=True)),
                dbc.Col(dbc.Card(card_content4, color="danger", inverse=True)),
            ],
            className="mb-4",
        ),
    
    
###########################################################################################################################
    
     dbc.Row([
         
         dbc.Col([
         
         dcc.Graph(id='map', figure=fig2),
         
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
         ),
     ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}
       
     ),

###########################################################################################################################
    
  dbc.Row([
         
         dbc.Col([
         
         dcc.Graph(id='bikeplot', figure=figLine),
         
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
         ),
     ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}
       
     ),



###########################################################################################################################

    dbc.Row(
            [
               
             dash_table.DataTable(
                 sort_action='native',
                data=StationBikesDF.to_dict('records'),
                        id='mydatatable',   
                 columns=[
            {'name': 'Station Name', 'id': 'stationname', 'type': 'text', 'editable': True},
            {'name': 'Total Racks', 'id': 'racksize', 'type': 'numeric', 'editable': True},
            {'name': 'Bikes in Station', 'id': 'countbikes', 'type': 'numeric', 'editable': True},
            {'name': 'Free Racks', 'id': 'availablespaces', 'type': 'numeric', 'editable': True},

        ],
        
                
        
        style_data_conditional=([
            
                
                {
                    'if': {
                        'filter_query': '{BikesinStation} < 5',
                        'column_id': 'Total Racks'
                    },
                    'backgroundColor': 'hotpink',
                    'font': 'bold'
                }
                

        ],),      
        ),    
                 
              
             
             ],style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'padding': '50px'}          
                
                    
             ),
    
], fluid=True)



if __name__ == "__main__": ####################################################################################################
    app.run_server(debug=True)################################################################################################


# In[ ]:





# In[ ]:




