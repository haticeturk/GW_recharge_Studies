# Groundwater Recharge Studies Map
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) 

An interactive web map of groundwater recharge studies, built with Python and Folium. It reads a CSV file of study metadata, converts coordinates into spatial objects, and produces an HTML map with multiple toggleable layers and custom legends.
Markers show study locations, data-availability status, tracer types, isotope methods and groundwater compartments. A Europe boundary overlay provides context.

## Files

- **interactive_map.py** – Python code code  
- **GW_Data_V2.csv**          – CSV of study metadata (DOI, coords, methods, etc.)  
- **world_countries.json**    – GeoJSON for country boundaries  

## Requirements

- Python 3.7+  
- Install dependencies with:
  ```bash
  pip install pandas geopandas folium shapely
  
git clone https://github.com/your-username/groundwater-map.git
cd groundwater-map
