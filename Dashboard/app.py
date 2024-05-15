import dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import json
import numpy as np
import plotly.express as px
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])
# df = pd.read_excel("WD_MAY_2022_UK_NC_provisional.xlsx")

# # Graphs
with open('merged_boroughs.geojson') as f:
    geojson_data = json.load(f)

# # # london_boroughs = ['Barking and Dagenham', 'Barnet', 'Bexley', 'Brent', 'Bromley', 'Camden', 'Croydon', 'Ealing',
# #                    'Enfield', 'Greenwich', 'Hackney', 'Hammersmith and Fulham', 'Haringey', 'Harrow', 'Havering',
# #                    'Hillingdon', 'Hounslow', 'Islington', 'Kensington and Chelsea', 'Kingston upon Thames', 'Lambeth',
# #                    'Lewisham', 'Merton', 'Newham', 'Redbridge', 'Richmond upon Thames', 'Southwark', 'Sutton', 'Tower Hamlets',
# #                    'Waltham Forest', 'Wandsworth', 'Westminster']
#
boroughs_names = [feature['properties']['name'] for feature in geojson_data['features']]
# print(boroughs_names)
# print(len(boroughs_names))
#
feat = geojson_data["features"][0]["geometry"]["coordinates"][0]
all_coordinates = np.array(feat)
mean_latitude = np.mean(all_coordinates[:, 1])
mean_longitude = np.mean(all_coordinates[:, 0])
print(mean_longitude, mean_latitude)

df = pd.read_csv("new_crime.csv")
df['Date'] = pd.to_datetime(df['Month'])
agg = df.groupby(['Borough']).count().reset_index()

fig = px.choropleth(data_frame=agg, geojson=geojson_data, locations=boroughs_names, featureidkey='properties.name',
                    center=dict(lon=mean_longitude, lat=mean_latitude), locationmode="geojson-id",  color=agg['Crime type'])
fig.update_geos(showland=True, landcolor='#FFFFFF', fitbounds="locations")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, )

fig_markers = px.scatter_geo(df[df['Borough']=='hackney'], lat='Latitude', lon='Longitude',
                             range_color='Crime type', hover_data=['Location', 'Crime type'],
                             size_max=20, opacity=0.5)

fig.add_trace(fig_markers.data[0])

# Wards map
# wards = df['WD22NM'].unique()

with open('wards.geojson') as f:
    wards_data = json.load(f)

wards_names = [feature['properties']['name'] for feature in wards_data['features']]

fig2 = px.choropleth(geojson=wards_data, locations=wards_names, featureidkey='properties.name',
                    center=dict(lon=mean_longitude, lat=mean_latitude), locationmode="geojson-id")
fig2.update_geos(fitbounds="locations")
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



# # LSOA map
# df = pd.read_csv("metropolitan-street-combined.csv")
# lsoa = df['LSOA name'].unique()
#
# with open('Lower_layer_Super_Output_Areas_2021_EW_BFC_V8_-8407643096148449625.geojson') as f:
#     lsoa_data = json.load(f)
#
# # lsoa = []
# # for feature in geojson_dict['features']:
# #     properties = feature.get('properties', {})
# #     lsoa.extend(properties.keys())
#
# fig3 = px.choropleth(geojson=lsoa_data, locations=lsoa, featureidkey='properties.name',
#                     center=dict(lon=mean_longitude, lat=mean_latitude), locationmode="geojson-id")
# fig3.update_geos(fitbounds="locations")
# fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# Customize Layout
app.layout = dbc.Container([
    # header
    dcc.Markdown("Data Challenge 2", style={'fontSize': 45, 'textAlign': 'center'}),

    # Short instructions for use
    dbc.Row([
        dbc.Col([
            html.Center(dcc.Markdown("Areas at risk of low trust and confidence")),
        ], width={"size": 8, "offset": 2}, align="centre")
    ], justify="centre"),

    # Map

    dbc.Row([
        dbc.Col([dcc.Graph(id='map-graph', figure=fig)
        ])
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='map-graph', figure=fig2)
        ])
    ])

    # dbc.Row([
    #     dbc.Col([dcc.Graph(id='map-graph', figure=fig3)
    #     ])
    # ])

], fluid=True)

# Run App
if __name__ == '__main__':
    app.run_server(port=8051, debug=False, use_reloader=False)
