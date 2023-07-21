import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import ast
import folium

COLUMNS = ['CASE#', 'DATE  OF OCCURRENCE', ' PRIMARY DESCRIPTION', ' SECONDARY DESCRIPTION', ' LOCATION DESCRIPTION',
           'ARREST', 'LATITUDE', 'LONGITUDE', 'LOCATION']

CRS = 'EPSG:4326'
class CrimeMap:
    # Attributes of the map
    def __init__(self, data_file, num_rows_to_display, center, zoom_start):
        self.data_file = data_file
        self.study_columns = COLUMNS
        self.num_rows_to_display = num_rows_to_display
        self.center = center
        self.crs = CRS
        self.zoom_start = zoom_start

    def read_data(self):
        """ Reads the csv file and returns contents"""
        file = pd.read_csv(self.data_file, usecols=self.study_columns)
        return file

    def split_data_time(self, data):
        """Takes the contents of the read file, selects the target date of occurrence column,
        splits the date and time to two columns,drops the original column, mergers the date and,
        time column to original dataframe, drops Nan rows from the LOCATION column and returns final data.
         """
        date_time_column = data['DATE  OF OCCURRENCE']
        date_time_df = date_time_column.to_frame()
        date_time_df[['Date', 'Time']] = date_time_df['DATE  OF OCCURRENCE'].str.split(' ', expand=True)
        date_time_df['Date'] = pd.to_datetime(date_time_df['Date'], format='%m/%d/%Y')
        date_time_df['Time'] = pd.to_datetime(date_time_df['Time'], format='%H:%M').dt.time
        date_time_df.drop(columns=['DATE  OF OCCURRENCE'], inplace=True)
        final_data = pd.concat([date_time_df, data], axis=1)
        final_data.drop(columns=['DATE  OF OCCURRENCE'], inplace=True)
        final_data.dropna(subset=['LOCATION'], inplace=True)
        return final_data

    def extract_geometry(self, data):
        """Takes the location column and converts it to a tuple, and uses it as a geometry.
        The point geometry is returned as GeoDataFrame
        """
        location_col = data['LOCATION'].apply(ast.literal_eval)
        location_df = location_col.to_frame()
        geometry = [Point(lat, lon) for lon, lat in location_df['LOCATION']]
        location_gdf = gpd.GeoDataFrame(location_df, geometry=geometry, crs=self.crs)
        location_gdf.drop(columns=['LOCATION'], inplace=True)
        return location_gdf

    def create_map(self, location_gdf):
        """Creates the point visualization using folium by isolating row tuple values to x and y coordinate
        """
        crime_location = folium.Map(location=self.center, zoom_start=self.zoom_start)
        for idx, row in location_gdf.head(self.num_rows_to_display).iterrows():
            lat, lon = row['geometry'].y, row['geometry'].x
            folium.Marker([lat, lon]).add_to(crime_location)
        return crime_location

    def save_map(self, crime_location, output_file):
        """"Creates a map of the point location and exports it as html for visualization"""
        crime_location.save(output_file)
