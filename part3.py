import sqlite3
import part1
import pandas as pd

from matplotlib import pyplot as plt



def verify_computed_distance(conn, csv_path="geodesic_distances.csv"):
    """
    Compare the flight distances stored in the database with geodesic distances from a CSV file.
    
    Params:
    - conn: connection to the SQLite database.
    - csv_path (str): Path to the geodesic distances CSV file.
    
    Returns:
    - merged_df (DataFrame): DataFrame containing flight distances and geodesic distances.
    """
    
    flights_df = pd.read_sql_query("SELECT origin, dest, distance FROM flights;", conn)
    
    # Load the geodesic distances from CSV
    geodesic_df = pd.read_csv(csv_path)

    # Rename columns to match for easier merging
    geodesic_df.rename(columns={"airport1": "origin", "airport2": "dest", "distance_m": "geodesic_distance"}, inplace=True)

    # Merge both DataFrames on origin and destination
    merged_df = flights_df.merge(geodesic_df, on=["origin", "dest"], how="left")

    # Compute the difference between actual and computed distances
    merged_df["difference"] = merged_df["distance"] - merged_df["geodesic_distance"]

    # Save results to CSV
    merged_df.to_csv("distance_comparison.csv", index=False)

    print("Comparison complete! Check 'distance_comparison.csv' for full results.")

    return merged_df.head()

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

def visualize_flight_destinations(conn, month, day, airport):
    """Generate a map of all destinations from a given NYC airport on a specific day."""
    pass

def get_flight_statistics():
    """Return statistics such as flight count, unique destinations, and most frequent destination."""
    pass


'''
Parameters:
    departure -> faa code for airport the flight is departing from
    arrival -> faa code for the airport the flight will be arriving at
'''
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

    delay_dict = {} #Empty dictionary to hold delay times for each airline

    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()

    query1 = f'SELECT * FROM airlines'
    query2 = f'SELECT dep_delay, carrier FROM flights'

    cursor.execute(query1)
    airlines_df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) 
    airlines_df.index = airlines_df['carrier'] #Sets airline dataframe indexes to be their carrier

    cursor.execute(query2)
    flights_df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])

    airline_set = set(airlines_df['carrier']) #Creates set of airline carriers, getting all the names with no duplicants

    # Iterates through each carrier
    for carrier in airline_set:
        filtered_flights = flights_df[flights_df['carrier'] == carrier] #Filteres flight dataframe by that carrier

        sum = filtered_flights['dep_delay'].sum() #Gets the sum of all the delays for that carrier
        total = filtered_flights['dep_delay'].size #Gets the total number of flights for that carrier

        average = round(sum / total, 2) #Calculates the average for each carrier and rounds it to 2 decimal places

        name = airlines_df.loc[carrier] #Gets the full airline name by the carrier index
        delay_dict[name[1]] = average #Adds the carrier to the dictionary and sets its value to the average delay time

    #Sets up pyplot
    plt.figure(figsize=(7,7))
    plt.bar(delay_dict.keys(), delay_dict.values()) #Sets the x-axis as the keys of the dictonary(carrier names) and y-axis as the values(averages)
    plt.xlabel('Airline Carriers')
    plt.ylabel('Average Delay Time')
    plt.title('Delay Times for Airlines')
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom = 0.3) 
    plt.show()

    
'''
Parameters:
    months -> range of months as a list of integers ([January, Febuary] --> [1,2])
    dest -> faa code for the destination airport
'''
def delayed_flights_by_destination(months, dest):
    """Return the number of delayed flights to a given destination within a specified time range."""
    
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()

    query1 = f'SELECT month,dep_delay,dest FROM flights'

    cursor.execute(query1)

    flights_df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) #Creates dataframe from flights table
    
    # Filters the flights dataframe by destination airport and if the flight is in the given range of months
    flights_df = flights_df[flights_df['dest'] == dest]
    flights_df = flights_df[flights_df['month'].isin(months)]

    delays = list(flights_df['dep_delay']) #Creates a list from departure delay column of dataframe
    
    delayed_flights = 0 #Counter for number of delayed flights
    # Iterates through each delay value
    for num in delays:
        #If the value is positive that means a delay occurred and the delayed flight counter will be increased by 1
        if num > 0:
            delayed_flights += 1

    return delayed_flights # Returns the total number of delayed flights

'''
Parameters:
    dest -> faa code for destination airport
'''
def top_airplane_manufacturers(dest):
    """Return the top 5 airplane manufacturers with planes departing to the specified destination."""
    
    lst = []

    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()

    query1 = f'SELECT tailnum, dest FROM flights'
    cursor.execute(query1)
    flights_df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) #Dataframe of flights data
    
    query2 = f'SELECT tailnum, manufacturer FROM planes'
    cursor.execute(query2)
    planes_df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description]) #Dataframe of planes data

    flights_df = flights_df[flights_df['dest'] == dest] #Fliters the flights dataframe based on the given desitnation airport
    
    tailnum_lst = list(flights_df['tailnum']) #Creates a list of all the tailnum values in the filtered flights dataframe

    manufacturers = set(planes_df['manufacturer']) #Gets all the names of the manufacturers in the planes dataframe

    # Iterates throught each manufacture
    for man in manufacturers:
        #Filters the plane data frame based on the the current manufacturer and if the tailnum is from a flight to given destination
        df = planes_df[planes_df['manufacturer'] == man]
        df = df[df['tailnum'].isin(tailnum_lst)]

        lst.append((df.size,man)) # Adds a tuple to a list in the form (number of planes creates, manufacturer)

    lst.sort(reverse=True,key=lambda tup: tup[0]) #Sorts list from high to low based on number of planes created by the manufacturer
    
    #Creates a list of the top five manufacturer names
    rtn_lst = []
    for i in range(5):
        rtn_lst.append(lst[i][1])
    
    return rtn_lst #Returns the list of top 5 manufacturers

    

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