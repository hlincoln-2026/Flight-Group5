import sqlite3
import part1
import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
import seaborn as sns

def get_df_from_database(query):
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])
    return df

def get_faa(name):
    query = f'SELECT faa,name FROM airports'
    df = get_df_from_database(query)

    row = df.loc[df['name'] == name, 'faa'].item()
    return row

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

def get_nyc_names(codes):
    query = f'SELECT name, faa FROM airports'
    df = get_df_from_database(query)

    df = df[df['faa'].isin(codes)]
    return list(df['name'])

def get_nyc_airports():
    """Retrieve all NYC airports from the database."""
    
    
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT origin FROM flights')

    df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])

    airport_set = set(df['origin'])
    conn.close()
    return get_nyc_names(airport_set)


def visualize_flight_destinations(month_x, day_x, nyc_airport):
    """Generate a map of all destinations from a given NYC airport on a specific day, with airline info as hover text."""
    

    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()


    query = """
    SELECT flights.dest, flights.carrier, 
           airports.lat AS dest_lat, airports.lon AS dest_lon, 
           airlines.name AS airline_name
    FROM flights
    JOIN airports ON flights.dest = airports.faa
    JOIN airlines ON flights.carrier = airlines.carrier
    WHERE flights.month = ? AND flights.day = ? AND flights.origin = ?;
    """

    df = pd.read_sql_query(query, conn, params=(month_x, day_x, nyc_airport))

    # Get origin airport coordinates
    origin_query = "SELECT lat, lon FROM airports WHERE faa = ?;"
    origin_data = pd.read_sql_query(origin_query, conn, params=(nyc_airport,))

    # Close connection
    conn.close()

    # Check if flights exist
    if df.empty:
        print(f"No flights found from {nyc_airport} on {month_x}/{day_x}")
        return
    
    if origin_data.empty: # also check if theere areany flights for that nyc airport
        print(f"Origin airport {nyc_airport} not found in airports table.")
        return
    
    start_lat = origin_data["lat"].iloc[0]
    start_lon = origin_data["lon"].iloc[0]

    # Assign unique colors to airlines, for better visibility
    airlines_colors = {airline: f"rgb({i*30 % 255}, {(i*60) % 255}, {(i*90) % 255})" for i, airline in enumerate(df["airline_name"].unique())}


    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=[start_lon], lat=[start_lat],
        mode='markers',
        name=nyc_airport,
        marker=dict(color='red', size=10),
        text=f"Origin: {nyc_airport}",
        hoverinfo="text",
        showlegend=True
    ))

    # Plot destinations and flight paths with airline info
    for _, row in df.iterrows():
        airline_info = f"Flight to {row['dest']}<br>Airline: {row['airline_name']}" #
        color = airlines_colors[row["airline_name"]]

        fig.add_trace(go.Scattergeo(
            lon=[row["dest_lon"]],
            lat=[row["dest_lat"]],
            mode='markers',
            name=row["airline_name"],  # Airline name in the legend
            marker=dict(color=color, size=8),
            text=airline_info, 
            hoverinfo="text",
            showlegend=True
        ))

        fig.add_trace(go.Scattergeo(
            lon=[start_lon, row["dest_lon"]],
            lat=[start_lat, row["dest_lat"]],
            mode='lines',
            line=dict(color=color, width=1),
            text=airline_info, 
            hoverinfo="text",
            showlegend=False
        ))


    fig.update_layout(
        title=f"Flight Destinations from {nyc_airport} on {month_x}/{day_x}", # title using airport and date
        geo=dict(projection_type="natural earth", showcoastlines=True),
        legend_title="Airlines"
    )


    fig.show()


def get_flight_statistics(month_x, day_x, nyc_airport):
    """Retrieve flight statistics for a given date and airport in NYC."""


    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()


    query = f'''
    SELECT dest, carrier, dep_delay, distance
    FROM flights
    WHERE month = {month_x} AND day = {day_x} AND origin = '{nyc_airport}';
    '''

    cursor.execute(query)
    flights = pd.DataFrame(cursor.fetchall(), columns=[x[0] for x in cursor.description])

    # Close connection
    conn.close()

    if flights.empty:
        print(f"No flight data available for {nyc_airport} on {month_x}/{day_x}")
        return
    
    # Number of flights and unique destinations
    total_flights = len(flights)
    unique_destinations = flights["dest"].nunique()

    # Most and least visited destinations
    most_visited = flights["dest"].value_counts().idxmax()
    least_visited = flights["dest"].value_counts().idxmin()


    # Find furthiest and closest destinations
    furthest_dest = flights.loc[flights["distance"].idxmax(), "dest"]
    closest_dest = flights.loc[flights["distance"].idxmin(), "dest"]

    # Busiest airline
    busiest_airline = flights["carrier"].value_counts().idxmax()

    # Compile results in a dicttionarry
    stats = {
        "Total Flights": total_flights,
        "Unique Destinations": unique_destinations,
        "Most Visited Destination": most_visited,
        "Least Visited Destination": least_visited,
        "Busiest Airline": busiest_airline,
        "Furthest Destination": furthest_dest,
        "Closest Destination": closest_dest
    }

    return stats #Returns the dictionary with the statistics for the day and airport


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

    # #Sets up pyplot
    # plt.figure(figsize=(7,7))
    # plt.bar(delay_dict.keys(), delay_dict.values()) #Sets the x-axis as the keys of the dictonary(carrier names) and y-axis as the values(averages)
    # plt.xlabel('Airline Carriers')
    # plt.ylabel('Average Delay Time')
    # plt.title('Delay Times for Airlines')
    # plt.xticks(rotation='vertical')
    # plt.subplots_adjust(bottom = 0.3) 
    # plt.show()

    return delay_dict

    
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
    conn = sqlite3.connect('flights_database.db')

    # Query to select distance and arr_delay where both columns have a non-null value for that entry.
    query = """
    SELECT distance, arr_delay
    FROM flights
    WHERE arr_delay IS NOT NULL AND distance IS NOT NULL;
    """

    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()

    # Get summary statistics of the data frame, specifically the count, mean, standard deviation, minimum, Q1, median, Q3, and maximum for distance and arr_delay
    print(df.describe())

    # Set up the scatter plot
    plt.figure(figsize=(10,6))
    sns.scatterplot(x='distance', y='arr_delay', data=df, alpha=0.5)
    plt.title('Flight Distance vs Arrival Delay Time')
    plt.xlabel('Distance (miles)')
    plt.ylabel('Arrival Delay Time (minutes)')
    plt.grid(True)

    # Display the scatter plot
    plt.show()

    # Compute the correlation between distance and arr_delay
    correlation = df['distance'].corr(df['arr_delay'])
    # Print out the correlation
    print(f"Correlation coefficient between flight distance and arrival delay time: {correlation:.2f}")
   
def calculate_average_plane_speed():
    """Calculate the average speed (in mph) for each plane model.
    and update the speed column in the planes table."""

    
    conn = sqlite3.connect('flights_database.db')

    flights_df = pd.read_sql_query("SELECT tailnum, distance, air_time FROM flights WHERE air_time > 0", conn)
    planes_df = pd.read_sql_query("SELECT tailnum, model, speed FROM planes", conn)

    # Compute the average speed per tailnum (aircraft)
    flights_df["speed"] = flights_df["distance"] / (flights_df["air_time"] / 60)  # Convert air_time to hours
    avg_speeds = round((flights_df.groupby("tailnum")["speed"].mean().reset_index()), 4)  # Average speed per tailnum and round to 4dp

    # Merge the new speeds with planes DataFrame
    planes_df = planes_df.merge(avg_speeds, on="tailnum", how="left")

    # # Rename columns correctly, after merging the tables the columns came out as speed_y(the average speed calculated), speed_x(old speed(0))
    planes_df.rename(columns={"speed_y": "speed", "speed_x": "old_speed"}, inplace=True)

    # Drop the old speed column 
    planes_df.drop(columns=["old_speed"], inplace=True)

    # Remove rows where speed couldn't be calculated
    planes_df.dropna(subset=["speed"], inplace=True)

    #  Update the database with the computed speeds
    for index, row in planes_df.iterrows():
        conn.execute("UPDATE planes SET speed = ? WHERE tailnum = ?", (row["speed"], row["tailnum"]))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Speed column updated successfully in planes table using Pandas.")



def compute_flight_directions(conn):
    """
    Determine the flight direction (direction_x, direction_y) for each flight
    """

    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE flights ADD COLUMN direction_x REAL")
    except sqlite3.OperationalError:
        pass  

    try:
        cursor.execute("ALTER TABLE flights ADD COLUMN direction_y REAL")
    except sqlite3.OperationalError:
        pass  

    # 1) JOIN flights->airports (origin) and flights->airports (dest)
    query = """
        SELECT 
            f.rowid AS flight_rowid,
            f.origin, 
            f.dest,
            a1.lat AS origin_lat,
            a1.lon AS origin_lon,
            a2.lat AS dest_lat,
            a2.lon AS dest_lon
        FROM flights AS f
        JOIN airports a1
          ON f.origin = a1.faa
        JOIN airports a2
          ON f.dest   = a2.faa
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No flights/airports data found. Check your joins or data.")
        return df
    
    # 2) Compute direction as simple difference in lon and lat

    df['direction_x'] = df['dest_lon'] - df['origin_lon']
    df['direction_y'] = df['dest_lat'] - df['origin_lat']
    
    # 3) Update 'flights' table with direction_x, direction_y 
    update_data = df[['direction_x','direction_y','flight_rowid']].values.tolist()
    
    try:
        cursor.executemany("""
            UPDATE flights
               SET direction_x = ?,
                   direction_y = ?
             WHERE rowid = ?
        """, update_data)
        conn.commit()
        print("Updated flights.direction_x, flights.direction_y successfully.")
    except sqlite3.OperationalError as e:
        print("Could not update flights table with direction_x/direction_y. Check if columns exist.")
        print("Error:", e)
    finally:
        cursor.close()

    return df

def compute_wind_effect_on_flights(conn):

    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE flights ADD COLUMN wind_effect REAL")
    except sqlite3.OperationalError:
        pass  

    query = """
        SELECT
            f.rowid AS flight_rowid,
            f.origin,
            f.dest,
            f.direction_x,
            f.direction_y,
            -- no more origin_lon, dest_lon, etc. needed 
            w.wind_speed,
            w.wind_dir
        FROM flights AS f
        JOIN weather AS w
          ON f.origin = w.origin
         AND f.year   = w.year
         AND f.month  = w.month
         AND f.day    = w.day
         AND f.hour   = w.hour
    """

    df = pd.read_sql_query(query, conn)
    if df.empty:
        print("No joined weather/flight data found. Check your JOIN conditions.")
        return df

    # Convert wind_dir to radians
    df['wind_dir_radians'] = np.radians(df['wind_dir'])
    df['wind_x'] = df['wind_speed'] * np.sin(df['wind_dir_radians'])
    df['wind_y'] = df['wind_speed'] * np.cos(df['wind_dir_radians'])

    # Dot product with direction_x, direction_y
    df['wind_effect'] = df['direction_x'] * df['wind_x'] + df['direction_y'] * df['wind_y']

    print(df[['flight_rowid','origin','dest','wind_speed','wind_dir','wind_effect']].head())

    update_data = df[['wind_effect','flight_rowid']].values.tolist()
    try:
        cursor.executemany("UPDATE flights SET wind_effect = ? WHERE rowid = ?", update_data)
        conn.commit()
        print("Wind effect computed and stored in flights.wind_effect.")
    except sqlite3.OperationalError as e:
        print("Could not update flights table with wind_effect.")
        print("Error:", e)
    finally:
        cursor.close()

    return df

def analyze_wind_effect_on_air_time(conn):
    """
    Analyze if the wind effect (dot product between flight direction and wind vector)
    has a relationship with air time. Specifically, we check whether flights with
    a positive wind effect (tailwind) differ in average air time from those with
    a negative wind effect (headwind).
    """

    # 1) Query the flights table for wind_effect, air_time
    query = """
        SELECT wind_effect, air_time
          FROM flights
         WHERE wind_effect IS NOT NULL
           AND air_time    IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)

    # If the table or columns are empty, just return
    if df.empty:
        print("No data found with both wind_effect and air_time.")
        return

       # 2) Split the DataFrame into positive and negative subsets
    df_pos = df[df['wind_effect'] >= 0]
    df_neg = df[df['wind_effect'] < 0]

    # 3) QQ-plots 
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    fig.suptitle('Wind Effect vs. Air Time (Tailwind vs. Headwind)')

    # --- PLOT 1: Positive (Tailwind) ---
    axs[0].scatter(df_pos['wind_effect'], df_pos['air_time'],
                   color='blue', alpha=0.5)
    axs[0].set_title('Positive Wind Effect (Tailwind)')
    axs[0].set_xlabel('Wind Effect (Dot Product)')
    axs[0].set_ylabel('Air Time (minutes)')
    axs[0].grid(True)

    # --- PLOT 2: Negative (Headwind) ---
    axs[1].scatter(df_neg['wind_effect'], df_neg['air_time'],
                   color='red', alpha=0.5)
    axs[1].set_title('Negative Wind Effect (Headwind)')
    axs[1].set_xlabel('Wind Effect (Dot Product)')
    axs[1].grid(True)

    plt.tight_layout()
    plt.show()
