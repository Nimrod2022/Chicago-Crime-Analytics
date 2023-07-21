
from data_processing import CrimeMap

# Map variables
data_file = "chicago crime data.csv"
output_file = "crime_map.html"
num_rows_to_display = 300
center_coordinates = [41.8781, -87.6298]
zoom_start = 10

# Instance of the CrimeMap
crime_map = CrimeMap(data_file=data_file, num_rows_to_display=num_rows_to_display, center=center_coordinates,
                     zoom_start=zoom_start)

data = crime_map.read_data()
final_data = crime_map.split_data_time(data)
location_gdf = crime_map.extract_geometry(final_data)
crime_location = crime_map.create_map(location_gdf)
crime_map.save_map(crime_location, output_file)
