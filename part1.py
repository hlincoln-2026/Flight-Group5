import plotly.express as px
import plotly.graph_objects as go


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
    fig.show()

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
        color='alt'
    )

    fig.update_layout(
            geo_scope='usa',
        )
    fig.show()

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
    fig.show()
    
    fig = go.Figure(data=[map])

    fig.show()



