# %%
# Import necessary libraries for data processing and mapping
import pandas as pd  # pandas: read CSV and handle tabular data
import geopandas as gpd  # geopandas: spatial data structures (GeoDataFrame)
import folium  # folium: create interactive Leaflet maps
from shapely.geometry import Point, LineString, Polygon  # shapely: build geometric objects
from shapely import wkt  # shapely.wkt: parse Well-Known Text geometries
from folium import plugins  # folium.plugins: extra map functionality (clusters, heatmaps)
import os
#Set the working directory

os.chdir("../GW_Studies")

# Specify the coordinate reference system (CRS) using EPSG code
crs = 4386

# Initialize the Folium map centered at the starting coordinates
start_coords = [46.81, 8.22]  # [latitude, longitude] for initial view
ISOmap = folium.Map(
    location=start_coords,   # center map here
    zoom_start=5.2,          # starting zoom level
    tiles='cartodbpositron', # default light basemap
    control_scale=True       # show a scale bar
)

# Add multiple base map tile layers for toggling

# Add multiple base map tile layers for toggling
for style in ['cartodbpositron', 'openstreetmap', 'stamenwatercolor', 'stamenterrain', 'Cartodb dark_matter']:
    folium.TileLayer(style).add_to(ISOmap)

# Create FeatureGroups for on/off toggling of overlay layers
General_Info_layer    = folium.FeatureGroup(name='Study_Information', show=True)  # study metadata
Data_avalibility      = folium.FeatureGroup(name='Data_Avalibility', show=True)  # data availability
Isotope_Type_layer    = folium.FeatureGroup(name='Tracers', show=True)           # tracer types
GW_layer              = folium.FeatureGroup(name='GW_Compartment', show=True)    # groundwater compartments
Sampling_Method_layer = folium.FeatureGroup(name='Isotope_Method', show=True)    # isotope analysis methods
EUROPE_layer          = folium.FeatureGroup(name='Europe', show=True)            # Europe boundary

# %%
# Load and clean groundwater study data
GW_data = pd.read_csv('./Data/GW_Data_V2.csv', sep=',')  # read CSV file
GW_data = GW_data.dropna()  # drop rows with any missing values

#Rename the columns
GW_data.rename(columns = {'DOI':'DOI', 'REVIEWER':'REVIEWER', 'DATA AVAILABILITY':'DATAAVAILABILITY', 'TRACERS':'TRACERS', 
                         'ISOTOPE-METHOD':'ISOTOPEMETHOD', 'COMPARTMENT':'COMPARTMENT', 'COUNTRY':'COUNTRY', 'CATCHMENT':'CATCHMENT', 
                         'LATITUDE':'LATITUDE', 'LONGITUDE':'LONGITUDE', 'ELEVATION':'ELEVATION', 'GEOLOGICAL SYSTEM':'GEOLOGICALSYSTEM', 
                         'MODEL':'MODEL', 'STUDY LENGTH':'STUDYLENGTH', 'SAMPLING FREQUENCY':'SAMPLINGFREQUENCY', 'OBJECTIVE':'OBJECTIVE', 
                         'KEYWORDS':'KEYWORDS'}, inplace = True)
# Create point geometries
geometry = gpd.points_from_xy(GW_data.LONGITUDE, GW_data.LATITUDE)
#Convert data to a GeoDataFrame
geo_df = gpd.GeoDataFrame(GW_data[['DOI','REVIEWER',	'DATAAVAILABILITY', 'TRACERS',	'ISOTOPEMETHOD',	'COMPARTMENT',
                                   'COUNTRY',	'CATCHMENT', 'LATITUDE',	'LONGITUDE',	'ELEVATION',	'GEOLOGICALSYSTEM',
                                   'MODEL',	'STUDYLENGTH',	'SAMPLINGFREQUENCY',	'OBJECTIVE',	'KEYWORDS']], geometry=geometry)


# %%
# (Optional) Extract simple [lat, lon] list from geometries
geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]
# %%
# Add detailed study markers to the Study_Information layer
for i in range(len(geo_df)):
    profiles = ''
    for info in geo_df.loc[i,['COUNTRY','GEOLOGICALSYSTEM','ELEVATION', 'ISOTOPEMETHOD', 'TRACERS', 'MODEL', 'STUDYLENGTH',	'SAMPLINGFREQUENCY']]:
        item = '<{0}>{1}</{0}>'.format('li',info)
        profiles += item
    html=f"""
        <h1>{geo_df.iloc[i]['CATCHMENT']}</h1>
        <p>OBJECTIVE:</p>
        {geo_df.iloc[i]['OBJECTIVE']}
          <p>KEYWORDS:</p>
        {geo_df.iloc[i]['KEYWORDS']}
        <p>DATA_AVAILABILITY and TYPE:</p>
         <ul> 
        {geo_df.iloc[i]['DATAAVAILABILITY']}
        </ul>
        {geo_df.iloc[i]['TRACERS']}
        <p>COUNTRY, GEOLOGICALSYSTEM, ELEVATION, ISOTOPEMETHOD, TRACERS, MODEL, STUDYLENGTH,SAMPLINGFREQUENCY:</p> 
        <ul>
        {profiles}
        </ul>
        </p>
        <p>Here is the paper  <a href="{geo_df.iloc[i]['DOI']}" target = "_blank">link </a></p>
        """
    iframe = folium.IFrame(html=html, width=1000, height=750)
    popup = folium.Popup(iframe, max_width=3650)
    folium.Marker(
        location=[geo_df.iloc[i]['LATITUDE'], geo_df.iloc[i]['LONGITUDE']],
        popup=  popup,
        icon=folium.DivIcon(html=f"""
            <div><svg>
                <rect x="20", y="20" width="15" height="15", fill="#56B4E9", opacity="1.0" />
            </svg></div>""")
     ).add_to(General_Info_layer)
# Add Data Availability layer with colored circle markers
for i in range(len(geo_df)):
    # assign a color marker for the type ofTracer
    if geo_df.iloc[i]['DATAAVAILABILITY'] == 'Yes (e.g., in repository or paper)':
        color = '#009E73'
    elif geo_df.iloc[i]['DATAAVAILABILITY'] == 'Partly (upon request authors)':
        color = '#E69F00'
    else:
        color = '#662a5a'
    folium.CircleMarker(
        location=[geo_df.iloc[i]['LATITUDE'], geo_df.iloc[i]['LONGITUDE'] ],
        popup=  geo_df.iloc[i]['DATAAVAILABILITY'],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        opacity=1.0,
        fill_opacity=1,
        legend_name='Data_Avalibility'
    ).add_to(Data_avalibility)
      
# %%
# Add Tracers layer with distinct colors for each tracer type
for i in range(len(geo_df)):
    # assign a color marker for the type ofTracer
    if geo_df.iloc[i]['TRACERS'] == 'Stable water isotopes':
        color = '#009E73'
    elif geo_df.iloc[i]['TRACERS'] == 'Tritium':
        color ='orange'
    elif geo_df.iloc[i]['TRACERS'] == 'Electrical Conductivity':
        color ='#56B4E9'
    else:
        color = 'black'
    folium.CircleMarker(
        location=[geo_df.iloc[i]['LATITUDE'], geo_df.iloc[i]['LONGITUDE']],
        popup =  geo_df.iloc[i]['TRACERS'],
        icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue">{geo_df.iloc[i]['TRACERS']}</div>"""),
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1,
        legend_name='Tracers'
    ).add_to(Isotope_Type_layer)
#lets add Istope _method layer 
for i in range(len(geo_df)):
    # assign a color marker for the type ofTracer
    if geo_df.iloc[i]['ISOTOPEMETHOD'] == 'Laser Absorption Spectroscopy':
        color = '#009E73'
    elif geo_df.iloc[i]['ISOTOPEMETHOD'] == 'Isotope Ratio Mass Spectrometry':
        color ='#E69F00'
    else:
        color = '#56B4E9'
    folium.CircleMarker(
        location=[geo_df.iloc[i]['LATITUDE'], geo_df.iloc[i]['LONGITUDE']],
        popup =  geo_df.iloc[i]['ISOTOPEMETHOD'],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1,
        legend_name='Isotope_Method'
    ).add_to(Sampling_Method_layer)
#lets add GW compartment layer
for i in range(len(geo_df)):
    # assign a color marker for the type ofTracer
    if geo_df.iloc[i]['COMPARTMENT'] == 'Springs':
        color = '#009E73'
    elif geo_df.iloc[i]['COMPARTMENT'] == 'Deep Ground Water':
        color ='orange'
    elif geo_df.iloc[i]['COMPARTMENT'] == 'Shallow Ground Water':
        color ='#505555'
    else:
        color = '#662a5a'
    folium.CircleMarker(
        location=[geo_df.iloc[i]['LATITUDE'], geo_df.iloc[i]['LONGITUDE']],
        popup = geo_df.iloc[i]['COMPARTMENT'],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=1,
        legend_name='GW_Compartment'
    ).add_to(GW_layer)
    #lets add sampling method layer
#Add Countries to the map
world_geo = r'Data/world_countries.json'
# Add Europe boundary layer from GeoJSON file
folium.GeoJson(world_geo, style_function=lambda feature: {
        "fillColor":"#0b1925",
        "color": "#0b1925",
        "weight": 0.2,
        "dashArray": "1, 1"},).add_to(EUROPE_layer)


# %%
# Attach all FeatureGroups to the main map and add layer control widget
General_Info_layer.add_to(ISOmap)
Data_avalibility.add_to(ISOmap)
Sampling_Method_layer.add_to(ISOmap)
Isotope_Type_layer.add_to(ISOmap)
GW_layer.add_to(ISOmap)
EUROPE_layer.add_to(ISOmap)


# %%
# Add title and HTML legends for map aesthetics

map_title = "Groundwater Recharge Map"
title_html ='''
             <h3 align="center" style="font-size:20px"><b>Groundwater Recharge Studies Map</b></h3>
             '''
ISOmap.get_root().html.add_child(folium.Element(title_html))
#Add the legend to the map
Data_avalibility_legend_html = '''
<div style="position: fixed; 
             bottom: 10px; left: 380px; width: 120px; height: 150px; 
             border:3px solid grey; z-index:9999; font-size:10px; background-color:white; padding: 5px;">
    <div style="text-align: center; margin-bottom: 10px; font-weight: bold;">Data Availability</div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #009E73; width:10px; height:10px;"></div><span style="margin-left: 5px;">Yes</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #E69F00; width:10px; height:10px;"></div><span style="margin-left: 5px;">Partly(upon request authors)</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #662a5a; width:10px; height:10px;"></div><span style="margin-left: 5px;">No</span></div>
</div>
'''

Isotope_Method_legend_html = '''
<div style="position: fixed; 
             bottom: 10px; left: 255px; width: 120px; height: 150px; 
             border:2px solid grey; z-index:9999; font-size:10px; background-color:white; padding: 5px;">
    <div style="text-align: center; margin-bottom: 10px; font-weight: bold;">Isotope Method</div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #009E73; width:10px; height:10px;"></div><span style="margin-left: 5px;">Laser Absorption Spectroscopy</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #E69F00; width:10px; height:10px;"></div><span style="margin-left: 5px;">Isotope Ratio Mass Spectrometry</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #56B4E9; width:10px; height:10px;"></div><span style="margin-left: 5px;">Other</span></div>
</div>
'''

Tracer_legend_html = '''
<div style="position: fixed; 
             bottom: 10px; left: 130px; width: 120px; height: 150px; 
             border:2px solid grey; z-index:9999; font-size:10px; background-color:white; padding: 5px;">
    <div style="text-align: center; margin-bottom: 10px; font-weight: bold;">Tracers</div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #009E73; width:10px; height:10px;"></div><span style="margin-left: 5px;">Stable water isotopes</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: orange; width:10px; height:10px;"></div><span style="margin-left: 5px;">Tritium</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #56B4E9; width:10px; height:10px;"></div><span style="margin-left: 5px;">Electrical Conductivity</span></div>
     <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: black; width:10px; height:10px;"></div><span style="margin-left: 5px;">Multiple</span></div>
</div>
'''

GW_legend_html = '''
<div style="position: fixed; 
             bottom: 10px; left: 5px; width: 120px; height: 150px; 
             border:2px solid grey; z-index:9999; font-size:10px; background-color:white; padding: 5px;">
    <div style="text-align: center; margin-bottom: 10px; font-weight: bold;">GW Compartment</div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #009E73; width:10px; height:10px;"></div><span style="margin-left: 5px;">Springs</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: orange; width:10px; height:10px;"></div><span style="margin-left: 5px;">Deep Ground Water</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #505555; width:10px; height:10px;"></div><span style="margin-left: 5px;">Shallow Ground Water</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 2px;"><div style="background: #662a5a; width:10px; height:10px;"></div><span style="margin-left: 5px;">Other</span></div>
</div>
'''
ISOmap.get_root().html.add_child(folium.Element(Data_avalibility_legend_html))
ISOmap.get_root().html.add_child(folium.Element(Isotope_Method_legend_html))
ISOmap.get_root().html.add_child(folium.Element(Tracer_legend_html))
ISOmap.get_root().html.add_child(folium.Element(GW_legend_html))
#
folium.map.LayerControl('topright', collapsed=False).add_to(ISOmap)

# Save the interactive map to an HTML file
#ISOmap.save("Mapv3_map.html")
ISOmap

# %%
#ISOmap to html
ISOmap.save("GW_Study_Map.html")


# %%
