import sqlite3
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
import matplotlib.pyplot as plt



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


###########  Import missing temperature entries  for JFK, LGA, EWR  ###########


# Setup Open-Meteo client
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

DB_PATH = "flights_database.db"


# Define coordinates
airport_coords = {
    "JFK": {"latitude": 40.6398, "longitude": -73.7787},
    "LGA": {"latitude": 40.7769, "longitude": -73.8740},
    "EWR": {"latitude": 40.6895, "longitude": -74.1745}
}

def fetch_hourly_temperature(airport_code, lat, lon):
    """Fetch hourly temperature data from Open-Meteo API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()

        if not hourly or hourly.Variables(0).ValuesAsNumpy().size == 0:
            print(f"[WARNING] No data for {airport_code}")
            return pd.DataFrame()

        time_range = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        df = pd.DataFrame({
            "datetime": time_range,
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "airport": airport_code
        })
        df["date"] = df["datetime"].dt.date
        return df

    except Exception as e:
        print(f"[ERROR] Fetch failed for {airport_code}: {e}")
        return pd.DataFrame()

def aggregate_daily_temperatures(df):
    return df.groupby(["airport", "date"])["temperature_2m"].agg(
        temp_min="min",
        temp_avg="mean",
        temp_max="max"
    ).reset_index()

def get_openmeteo_daily_temperatures():
    all_data = []
    for code, coords in airport_coords.items():
        hourly = fetch_hourly_temperature(code, coords["latitude"], coords["longitude"])
        if not hourly.empty:
            all_data.append(aggregate_daily_temperatures(hourly))
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def load_weather_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    conn.close()
    return df

def merge_and_fill_weather(weather_df, temp_df):
    """Merge temperature data and fill missing temperature values (only for JFK, LGA, EWR)."""

    if weather_df.empty:
        print("[WARNING] Weather table from database is empty. Skipping merge.")
        return pd.DataFrame()

    if temp_df.empty:
        print("[WARNING] Open-Meteo temperature data is empty. Skipping merge.")
        return weather_df

    # Normalize keys for merging
    weather_df["origin"] = weather_df["origin"].str.strip().str.upper()
    temp_df["airport"] = temp_df["airport"].str.strip().str.upper()

    # Add 'date' to weather_df
    weather_df["date"] = pd.to_datetime({
        "year": 2023,
        "month": weather_df["month"],
        "day": weather_df["day"]
    }).dt.date

    # Merge: will only fill data for JFK, LGA, EWR
    merged = weather_df.merge(
        temp_df,
        left_on=["origin", "date"],
        right_on=["airport", "date"],
        how="left"
    )

    # Optional: fill missing `temp` only for matched rows
    if "temp_avg" in merged.columns:
        merged["temp"] = merged["temp"].fillna(merged["temp_avg"])

    # Debug
    matched_rows = merged["airport"].notna().sum()
    print(f"[INFO] Merged temperature data for {matched_rows} rows (out of {len(merged)}).")

    return merged


def ensure_weather_columns(conn):
    cursor = conn.cursor()
    for col in ['temp_min', 'temp_avg', 'temp_max']:
        try:
            cursor.execute(f"ALTER TABLE weather ADD COLUMN {col} REAL")
        except sqlite3.OperationalError:
            pass  # Already exists
    conn.commit()


def save_daily_temperatures_to_db(merged_df, db_path='flights_database.db'):
    """Adds temp_min, temp_avg, temp_max columns to the weather table and fills them."""

    print("[DEBUG] Columns in merged_df:", merged_df.columns.tolist())  # 🔍 DEBUG LINE

    required_cols = ["temp_min", "temp_avg", "temp_max", "origin", "month", "day"]
    for col in required_cols:
        if col not in merged_df.columns:
            print(f"[ERROR] Missing column in merged_df: {col}")
    #  Exit early if required columns are missing
    if not all(col in merged_df.columns for col in required_cols):
        print("[ABORT] Cannot proceed with saving to DB. Missing required columns.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add columns if not exist
    for col in ['temp_min', 'temp_avg', 'temp_max']:
        try:
            cursor.execute(f"ALTER TABLE weather ADD COLUMN {col} REAL")
        except sqlite3.OperationalError:
            pass

    # Prepare updates
    updates = merged_df[required_cols].dropna()

    update_query = """
        UPDATE weather
        SET temp_min = ?, temp_avg = ?, temp_max = ?
        WHERE origin = ? AND month = ? AND day = ?
    """
    cursor.executemany(update_query, updates.values.tolist())
    conn.commit()

    print(f"[INFO] Updated {cursor.rowcount} rows in weather table.")
    conn.close()


def verify_temperature_columns():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT origin, month, day, temp_min, temp_avg, temp_max FROM weather LIMIT 10", conn)
    conn.close()
    print(df.head())
    print(df[["temp_min", "temp_avg", "temp_max"]].isna().sum())
    return df



def main():
    weather_df = load_weather_from_db()
    temp_df = get_openmeteo_daily_temperatures()
    merged_df = merge_and_fill_weather(weather_df, temp_df)
    save_daily_temperatures_to_db(merged_df)
    verify_temperature_columns()

if __name__ == "__main__":
    main()
