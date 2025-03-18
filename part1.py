import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math



# Display all airports worldwide
# Parameters:
#   df --> DataFrame of flight data
# Output: Scatter Geo of all given airports on world map
# Return: None
def all_airports(df):
    fig = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        hover_name='name',  # Airport name will show on hover
        projection='natural earth',
        color='tzone'
    )
    return fig


# Display all international flights
# Parameters:
#   df --> DataFrame of flight data
# Output: Scatter Geo of airports outside of United States
# Return: None
def international_flights(df):
    us_airports = (
        (df['lat'].between(15, 72)) &
        (df['lon'].between(-180, -65))
    )

    non_us = df[~us_airports].copy()

    fig = px.scatter_geo(
        non_us,
        lat='lat',
        lon='lon',
        hover_name='name',
        projection='natural earth',
        color='name'
    )

    fig.show()


# Display flights only in the United States
# Parameters:
#   df --> DataFrame of flight data
# Output: Scatter Geo of airports only in United States
# Return: None
def only_usa(df):
    fig = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        hover_name='name',
        color='tzone'
    )

    fig.update_layout(
            geo_scope='usa',
        )
    
    return fig


# Display all flight paths from airports list
# Parameters: 
#   airports --> list of airports faa codes
#   df --> DataFrame of flight data
# Output: Scatter Geo with flight paths between JFK airport and all airports in given list
# Return: None
def flight_paths(airports, df):
    start_lat = 40.63980103
    start_lon = -73.77890015

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
            lon = [start_lon],
            lat = [start_lat],
            mode = 'markers',
            name="JFK",
            marker=dict(color='red'),
            showlegend=False
        ))
    
    destinations = df[df['faa'].isin(airports)]

    for i, dest in destinations.iterrows():

        fig.add_trace(go.Scattergeo(
            lon = [dest['lon']],
            lat = [dest['lat']],
            mode = 'markers',
            name=f"{dest['faa']}",
            marker=dict(color='blue'),
            showlegend=False
        ))

        fig.add_trace(go.Scattergeo(
            lon = [start_lon, dest['lon']],
            lat = [start_lat, dest['lat']],
            mode = 'lines',
            line=dict(color='green'),
            showlegend=False
        ))
    return fig


# Calculates the Euclidean Distance between two locations
# Parameters:
#   loc1 --> tuple of lat, lon values for location 1
#   loc2 --> tuple of lat, lon values for locations 2
# Output: None
# Return: Float of euclidean distance between two points
def euclidean_distance(loc1, loc2):
    diff1 = loc2[0] - loc1[0]
    diff2 = loc2[1] - loc1[1]
    return math.sqrt((diff1**2 + diff2**2))


# Creates list of Euclidean Distances between JFK and each airport given
# Parameters:
#   df --> DataFrame of flight data
#   airports --> list of faa codes for different airports
# Output: None
# Returns: list of distances
def calc_distances(df, airports):
    df = df[df['faa'].isin(airports)]
    print(df['faa'])
    jfk = (40.63980103, -73.77890015)
    distances = []

    for i, airport in df.iterrows():
        loc = (airport['lat'], airport['lon'])
        distance = euclidean_distance(jfk, loc)
        distances.append(distance)

    return distances


# Calculates and displays a histogram using euclidean distances between airports
# Parameters: 
#   df --> DataFrame of flight data
#   airports --> list of faa codes for different airports
# Output: Histogram diagram
# Return: None
def create_histogram(df, airports):
    lst = calc_distances(df, list(df['faa']))
    plt.hist(lst,bins=30,label='test',edgecolor='black')
    plt.ylabel('Distance Between JFK and Airport')
    plt.xlabel('Airport Index')
    plt.show()



R = 3958.8  # Earth's radius in miles


def calculate_geodesic_distance(lat1, lon1, lat2, lon2):
    """Calculates the geodesic distance between two airports using latitude and longitude.
    params: latitude and longitude of airport pairs.
    """

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # calculate differences
    delta_phi = lat2 - lat1
    delta_lamda = lon2 - lon1
    phi_m = (lat1 + lat2) / 2

    # geodesic distance
    distance = R * np.sqrt(
        (2 * np.sin(delta_phi/2) * np.cos(delta_lamda/ 2)) ** 2 +
        ( 2* np.cos(phi_m) * np.sin(delta_lamda / 2)) ** 2
    )

    return distance


def calculate_all_distances(df):
    distances = []

    for i , row1 in df.iterrows():
        for j , row2 in df.iterrows():
            if i != j:
                dist = calculate_geodesic_distance(row1['lat'], row1['lon'], row2['lat'], row2['lon'])
                distances.append({'airport1': row1['faa'], 'airport2': row2['faa'], 'distance_m': dist})
    
    return pd.DataFrame(distances)


