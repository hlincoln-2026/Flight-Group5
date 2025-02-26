import sqlite3
import part1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


def get_nyc_airports(conn):

    """Retrieve all NYC airports from the database.
    params: conn, a database connection
    returns: a dataframe of origin airports in NYC
    """

    query = """
    SELECT flights.*
    FROM flights
    INNER JOIN airports ON flights.origin = airports.faa
    WHERE airports.tzone = 'America/New_York'
    """
    results = pd.read_sql_query(query, conn)
    nyc_airports = results.drop_duplicates(subset=['origin']) 
    
    return nyc_airports   

def visualize_flight_destinations(conn, month, day, airport):
    """Generate a map of all destinations from a given NYC airport on a specific day."""
    pass

def get_flight_statistics():
    """Return statistics such as flight count, unique destinations, and most frequent destination."""
    pass

def get_airplane_usage():
    """Return a dictionary describing the number of times each plane type was used for a specific route."""
    pass

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