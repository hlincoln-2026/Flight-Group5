import sqlite3
import pandas as pd


'''
Look for duplicates in the flights table. Take into account that here a flight number can occur multiple times,
only count it as duplicate when the same flight appears multiple times.
'''

def find_duplicants():

    flights_dict = dict()

    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()

    query = f'SELECT * FROM flights'
    cursor.execute(query)

    flights = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])
    

    dups = flights.duplicated()
    if True in dups:
        print('There are duplicated flights')
    else:
        print('No Duplicant Flights')

    # flight_set = set(flights['flight'])
    # for num in flight_set:
    #     df = flights[flights['flight']==num]
    #     dups = df.duplicated()
    #     for i in dups:
    #         if i:
    #             print(i)

    # for i, j in flights.iterrows():
    #     flight_num = j.iloc[10]
    #     print(i)
    #     if flight_num in flight_set:
    #         flights_dict[flight_num] += 1
    #     else:
    #         flights_dict[flight_num] = 1
    #         flight_set.add(flight_num)
    
    # for key, value in flights_dict.items():
    #     print(f'{key}: {value}')


find_duplicants()

import numpy as np
import matplotlib.pyplot as plt



#Check for missing values in the flights table
def check_missing_values_flights(conn):
	pass

#Look for duplicates in the flights table
def find_duplicate_flights(conn):
	pass

#Convert scheduled and actual arrival/departure times to datetime objects
def convert_flight_times_to_datetime(conn):
	pass

#Check if the data in flights is in order (validate air time, departure time, etc.)
def validate_flight_data(conn):
    """
    Validate the 'flights' table for logical inconsistencies.

    Checks performed:
    - dep_time should match sched_dep_time + dep_delay
    - arr_time should match sched_arr_time + arr_delay
    - air_time should be consistent with arr_time - dep_time
    """

    query = """
        SELECT 
            rowid AS flight_rowid,
            year, month, day, 
            dep_time, sched_dep_time, dep_delay, 
            arr_time, sched_arr_time, arr_delay, 
            air_time
        FROM flights
    """

    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("No flight data found in the database.")
        return df


    # 1️ Validate Departure Time
    df['expected_dep_time'] = (df['sched_dep_time'] + df['dep_delay']).astype('Int64')
    df['dep_time_mismatch'] = df['dep_time'] != df['expected_dep_time']

    # 2️ Validate Arrival Time
    df['expected_arr_time'] = (df['sched_arr_time'] + df['arr_delay']).astype('Int64')
    df['arr_time_mismatch'] = df['arr_time'] != df['expected_arr_time']

    # 3️ Validate Air Time Consistency
    df['expected_air_time'] = (df['arr_time'] - df['dep_time']).astype('Int64')
    df['air_time_mismatch'] = df['air_time'] != df['expected_air_time']



    # 4️ Extract Rows with Inconsistencies
    inconsistent_flights = df[(df['dep_time_mismatch']) | (df['arr_time_mismatch']) | (df['air_time_mismatch'])]

    if inconsistent_flights.empty:
        print("All flights have consistent departure and arrival times.")
    else:
        print(f"Found {len(inconsistent_flights)} inconsistent flights.")
        print(inconsistent_flights[['flight_rowid', 'dep_time', 'sched_dep_time', 'dep_delay',
                                    'expected_dep_time', 'arr_time', 'sched_arr_time', 'arr_delay',
                                    'expected_arr_time', 'air_time', 'expected_air_time']])

    return inconsistent_flights



#Create a column for local arrival time considering time zone differences
def compute_local_arrival_time(conn):
    """
    Compute the local arrival time for each flight by adjusting `arr_time`
    using the time difference between departure and arrival airports.
    
    """

    cursor = conn.cursor()

    # Add 'local_arr_time' column if it does not exist
    try:
        cursor.execute("ALTER TABLE flights ADD COLUMN local_arr_time INTEGER")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # 1) JOIN flights with airports to get departure and arrival time zones
    query = """
        SELECT 
            f.rowid AS flight_rowid,
            f.origin, 
            f.dest,
            f.arr_time,
            a1.tz AS dep_tz,
            a2.tz AS arr_tz
        FROM flights AS f
        JOIN airports AS a1
          ON f.origin = a1.faa
        JOIN airports AS a2
          ON f.dest   = a2.faa
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No flights/airports data found. Check your joins or data.")
        return df
    
        # 2) Compute time difference
    df['time_diff'] = df['arr_tz'] - df['dep_tz']

    # 3) Convert `arr_time` from HHMM format to total minutes
    df['arr_time_hours'] = df['arr_time'] // 100
    df['arr_time_minutes'] = df['arr_time'] % 100
    df['arr_time_total_minutes'] = df['arr_time_hours'] * 60 + df['arr_time_minutes']

    # 4) Apply time difference in minutes
    df['local_arr_time_total_minutes'] = df['arr_time_total_minutes'] + (df['time_diff'] * 60)


    # 5) Convert back to HHMM format
    df['local_arr_time_hours'] = (df['local_arr_time_total_minutes'] // 60) % 24
    df['local_arr_time_minutes'] = df['local_arr_time_total_minutes'] % 60
    df['local_arr_time'] = df['local_arr_time_hours'] * 100 + df['local_arr_time_minutes']

    # Prepare data for update
    update_data = df[['local_arr_time', 'flight_rowid']].values.tolist()

    try:
        cursor.executemany("UPDATE flights SET local_arr_time = ? WHERE rowid = ?", update_data)
        conn.commit()
        # print("Updated flights.local_arr_time successfully.")
    except sqlite3.OperationalError as e:
        # print("Could not update flights table with local_arr_time. Check if column exists.")
        print("Error:", e)
    finally:
        cursor.close()

    return df

#Study the effect of wind or precipitation on different plane types
def analyze_weather_impact_on_planes(conn):
	pass

#Generate statistics for different departure and arrival airports
def generate_airport_statistics(conn, airport_code):
	pass

#Develop functions for general analysis in the dashboard (delays, speed, routes, weather relations, etc.)
def analyze_airport_delays(conn):
	pass
def analyze_fastest_flights(conn):
	pass
def analyze_most_frequent_routes(conn):
	pass
def analyze_weather_vs_delay(conn):
	pass

