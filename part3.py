import sqlite3
import part1
import pandas as pd


def verify_computed_distances():
    """Verify that the computed distances match the distances in the flights table."""
    pass

def get_nyc_airports():
    """Retrieve all NYC airports from the database."""
    nyc_lst = ['FOK','ISP','FRG','JFK','LGA','HPN','MGJ','SWF','BGM','ELM','ITH','JHW',
               'DKK','BUF','IAG','ROC','SYC','RME','ALB','SCH','GFL','ART','LKP','SLK','PBG','MSS','OGS']
    
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM airports')

    df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])

    df = df[df['faa'].isin(nyc_lst)]

    return df

    

def visualize_flight_destinations():
    """Generate a map of all destinations from a given NYC airport on a specific day."""
    pass

def get_flight_statistics():
    """Return statistics such as flight count, unique destinations, and most frequent destination."""
    pass

def get_airplane_usage(departure, arrival):
    """Return a dictionary describing the number of times each plane type was used for a specific route."""

    plane_dict = {'Fixed wing single engine': 0, 'Rotorcraft': 0, 'Fixed wing multi engine': 0}

    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()

    query1 = f'SELECT tailnum,origin,dest FROM flights'
    query2 = f'SELECT tailnum,type FROM planes'

    cursor.execute(query1)
    flights = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) #Creates dataframe with data from flights table

    cursor.execute(query2)
    planes = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) #Creates dataframe with data from planes table

    planes_lst = list(planes['tailnum']) #Makes list of all the 'tailnum' column from planes dataframe

    #Filters data in flights dataframe to only include flights from given origin to destination
    flights = flights[flights['origin'] == departure]
    flights = flights[flights['dest'] == arrival]

    #Iterates through each tailnum of the the filtered flights dataframe
    for flight in list(flights['tailnum']):
        #Increases the plane type counter in the dictionary if the flight has a tailnum in the planes dataframe
        if flight in planes_lst:
            plane_type = planes['type'].loc[planes_lst.index(flight)]
            plane_dict[plane_type] += 1


    return plane_dict #Returns the dictionary with the count of each plane type

    

def average_departure_delay():
    """Compute and visualize the average departure delay per airline."""
    pass

def delayed_flights_by_destination():
    """Return the number of delayed flights to a given destination within a specified time range."""
    pass

def top_airplane_manufacturers():
    """Return the top 5 airplane manufacturers with planes departing to the specified destination."""
    pass

def analyze_distance_vs_arrival_delay():
    """Investigate the relationship between flight distance and arrival delay time."""
    pass

def compute_average_plane_speeds():
    """Compute and update the average speed for each plane model in the database."""
    pass

def compute_flight_directions():
    """Determine the flight direction for each airport from NYC."""
    pass

def compute_wind_effect_on_flights():
    """Compute the inner product of flight direction and wind speed for given flights."""
    pass

def analyze_wind_effect_on_air_time():
    """Analyze if the wind effect has a significant impact on air time."""
    pass