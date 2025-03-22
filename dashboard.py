import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sqlite3
import part1
import part3
import part4


# ✅ Ensure `set_page_config` is the first Streamlit command
st.set_page_config(layout="wide")  # Must be the first command


############# flight statistics ############################

def get_airport_name(faa):
    """
    Given an FAA code, return the airport's name.
    Returns the FAA code itself if no matching record is found.
    """
    query = "SELECT name FROM airports WHERE faa = ?"
    conn = sqlite3.connect('flights_database.db')
    df = pd.read_sql_query(query, conn, params=(faa,))
    conn.close()

    if not df.empty:
        return df["name"].iloc[0]
    else:
        return faa  # Fallback if no record found


def get_flight_statistics():
    query = """
        SELECT origin, dest, carrier, distance
        FROM flights
    """
    df = get_df_from_database(query)

    if df.empty:
        st.warning("No flight data available.")
        return {}

    total_flights = len(df)
    unique_destinations = df['dest'].nunique()



    # Longest and shortest flights
    longest_flight = df.loc[df['distance'].idxmax()]
    shortest_flight = df.loc[df['distance'].idxmin()]

    longest_flight = f"{get_airport_name(longest_flight['origin'])} ({longest_flight['origin']})  → {get_airport_name(longest_flight['dest'])} ({longest_flight['dest']})"
    shortest_flight = f"{get_airport_name(shortest_flight['origin'])} ({shortest_flight['origin']})  → {get_airport_name(shortest_flight['dest'])} ({shortest_flight['dest']})"

    # Calculate the most and least frequent routes by grouping on both origin and destination
    route_counts = df.groupby(["origin", "dest"]).size()
    most_frequent_route_tuple = route_counts.idxmax()  # (origin, dest)
    least_frequent_route_tuple = route_counts.idxmin()  # (origin, dest)



    most_frequent_route = (
        f"{get_airport_name(most_frequent_route_tuple[0])} ({most_frequent_route_tuple[0]}) → "
        f"{get_airport_name(most_frequent_route_tuple[1])} ({most_frequent_route_tuple[1]})"
    )
    least_frequent_route = (
        f"{get_airport_name(least_frequent_route_tuple[0])} ({least_frequent_route_tuple[0]}) → "
        f"{get_airport_name(least_frequent_route_tuple[1])} ({least_frequent_route_tuple[1]})"
    )


    # Compute highest and lowest volume carriers
    carrier_counts = df['carrier'].value_counts()
    highest_volume_carrier = carrier_counts.idxmax()
    lowest_volume_carrier = carrier_counts.idxmin()
    highest_volume_carrier_name = get_carrier_name(highest_volume_carrier)
    lowest_volume_carrier_name = get_carrier_name(lowest_volume_carrier)

    stats = {
        "Total Flights": total_flights,
        "Unique Destinations": unique_destinations,
        "Most Frequent Route": most_frequent_route,
        "Least Frequent Route": least_frequent_route,
        "Highest Volume Carrier": highest_volume_carrier_name,
        "Lowest Volume Carrier": lowest_volume_carrier_name,
        "Longest Flight": longest_flight,
        "Shortest Flight": shortest_flight
    }
    
    return stats


def display_flight_statistics():
    """
    Displays flight statistics in a neat two-column table.
    """
    st.subheader("Flight Statistics (All Flights)")
    stats = get_flight_statistics()
    
    # Ensure highest/lowest volume carrier are strings
    highest_volume = stats["Highest Volume Carrier"]
    lowest_volume = stats["Lowest Volume Carrier"]
    if isinstance(highest_volume, pd.Series):
        highest_volume = highest_volume.iloc[0]
    if isinstance(lowest_volume, pd.Series):
        lowest_volume = lowest_volume.iloc[0]

    stats_table = pd.DataFrame({
        "Statistic": [
            "Total Flights", 
            "Unique Destinations", 
            "Most Frequent Route",
            "Least Frequent Route",
            "Highest Volume Carrier",
            "Lowest Volume Carrier",
            "Longest Flight",
            "Shortest Flight"
        ],
        "Value": [
            stats["Total Flights"],
            stats["Unique Destinations"],
            stats["Most Frequent Route"],
            stats["Least Frequent Route"],
            highest_volume,
            lowest_volume,
            stats["Longest Flight"],
            stats["Shortest Flight"]
        ]
    })
    st.table(stats_table)

################################### manufacturer stats per destination  ######################################################

def display_top_manufacturers_for_destination():
    """
    Displays a bar chart of the top 5 airplane manufacturers 
    for flights departing to a selected international destination.

    """
    st.header("International Airport Destination Manufacturer Analysis", divider="gray")
    
    # Retrieve only international airports (those with "international" in the name)
    airports_query = "SELECT faa, name FROM airports WHERE lower(name) LIKE '%international%'"
    airports_df = get_df_from_database(airports_query)
    
    # Let the user select a destination airport by name from the filtered international airports
    dest = st.selectbox("Select International Destination Airport", airports_df['name'], index=0, placeholder="Enter destination name")
    if dest:
        # Retrieve the FAA code for the selected destination
        faa = airports_df[airports_df['name'] == dest]['faa'].item()
        
        # Query flights with the selected destination FAA code
        query_flights = f"SELECT tailnum FROM flights WHERE dest = '{faa}'"
        flights_df = get_df_from_database(query_flights)
        
        if flights_df.empty:
            st.warning("No flights found for this destination.")
            return
        
        # Retrieve planes data including manufacturer information
        query_planes = "SELECT tailnum, manufacturer FROM planes"
        planes_df = get_df_from_database(query_planes)
        
        # Merge flights and planes data on tailnum
        merged_df = pd.merge(flights_df, planes_df, on="tailnum", how="left")
        
        if merged_df.empty or merged_df['manufacturer'].isnull().all():
            st.warning("No manufacturer data available for flights to this destination.")
            return
        
        # Count the number of flights per manufacturer
        manufacturer_counts = merged_df['manufacturer'].value_counts().reset_index()
        manufacturer_counts.columns = ['manufacturer', 'num_flights']
        
        # Calculate the percentage of flights for additional insight
        total = manufacturer_counts['num_flights'].sum()
        manufacturer_counts['percentage'] = (manufacturer_counts['num_flights'] / total * 100).round(2)
        
        # Select the top 5 manufacturers
        top5 = manufacturer_counts.head(5)
        
        # Create a bar chart using Plotly Express with extra hover data
        fig = px.bar(
            top5, 
            x="manufacturer", 
            y="num_flights", 
            title=f"Top 5 Manufacturers for {dest}",
            labels={"manufacturer": "Manufacturer", "num_flights": "Number of Flights"},
            text="num_flights",
            color="manufacturer",
            hover_data={"percentage": True}
        )
        
        fig.update_traces(
            texttemplate="%{text}",
            textposition="outside"
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig)

#################################### airline market share ############################

def display_airline_market_share():
    """
    Displays a horizontal bar chart showing the share of total flights for each airline,
    leveraging the airlines table for airline names.
    """

    query = """
        SELECT a.name AS airline_name,
               COUNT(*) AS num_flights
        FROM flights f
        JOIN airlines a ON f.carrier = a.carrier
        GROUP BY a.name
    """
    df = get_df_from_database(query)

    if df.empty:
        st.warning("No flight data available.")
        return


    df = df.sort_values("num_flights", ascending=False)

   
    total_flights = df["num_flights"].sum()
    df["percentage"] = (df["num_flights"] / total_flights * 100).round(2)

    # Create a horizontal bar chart 
    fig = px.bar(
        df,
        x="num_flights",
        y="airline_name",
        orientation="h",  # horizontal bars
        title="Airline Market Share (Total Flights)",
        labels={"num_flights": "Number of Flights", "airline_name": "Airline"},
        hover_data=["percentage"],  # show percentage on hover
        text="num_flights"          # display the number of flights on the bar
    )

    # Place the text inside or outside the bars as desired
    fig.update_traces(
        textposition="outside"
    )

    # Reverse the Y-axis so the largest bar is at the top
    fig.update_layout(
        yaxis=dict(autorange="reversed")
    )

    st.plotly_chart(fig)
####################################### MONTHLY FLIGHTS PER AIRLINE ######################
def display_flights_by_month():
    """
    Displays a bar chart showing flight counts by month, 
    optionally filtered by a selected airline.
    """
    st.header("Monthly Flight Trends", divider="gray")
    
    # Retrieve distinct airline names from the airlines table.
    query_airlines = "SELECT DISTINCT name FROM airlines"
    airlines_df = get_df_from_database(query_airlines)
    airline_options = ["All Airlines"] + sorted(airlines_df["name"].tolist())
    
    # Allow user to filter by airline.
    selected_airline = st.selectbox("Filter by Airline", airline_options, index=0)
    
    # Query flights to count flights by month.
    if selected_airline == "All Airlines":
        query_flights = """
            SELECT month, COUNT(*) AS num_flights 
            FROM flights 
            GROUP BY month 
            ORDER BY month
        """
        df = get_df_from_database(query_flights)
    else:
        # Retrieve the carrier code corresponding to the selected airline.
        query_carrier = f"SELECT carrier FROM airlines WHERE name = '{selected_airline}'"
        carrier_df = get_df_from_database(query_carrier)
        if carrier_df.empty:
            st.warning("Selected airline not found in airlines table.")
            return
        carrier_code = carrier_df.iloc[0]["carrier"]
        
        query_flights = f"""
            SELECT month, COUNT(*) AS num_flights 
            FROM flights 
            WHERE carrier = '{carrier_code}'
            GROUP BY month 
            ORDER BY month
        """
        df = get_df_from_database(query_flights)
    
    if df.empty:
        st.warning("No flight data available for the selected criteria.")
        return

    # Create a bar chart using Plotly Express
    fig = px.bar(
        df,
        x="month",
        y="num_flights",
        title=f"Flight Counts by Month {'(All Airlines)' if selected_airline == 'All Airlines' else f'for {selected_airline}'}",
        labels={"month": "Month", "num_flights": "Number of Flights"},
        text="num_flights"
    )
    
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    
    st.plotly_chart(fig)



################################ plane stats###############################################

def display_plane_statistics():
    """
    Updates the planes table with calculated average speeds
    and displays a bar chart showing the top 10 fastest plane models.
    """
    part3.calculate_average_plane_speed()

    # Retrieve the updated planes data (including manufacturer)
    query = "SELECT tailnum, model, speed, manufacturer FROM planes"
    planes_df = get_df_from_database(query)

    # Group by both model and manufacturer to get a single average speed per (model, manufacturer)
    planes_grouped = planes_df.groupby(["model", "manufacturer"], as_index=False)["speed"].mean()

    # Sort by speed descending and take top 10
    top_planes = (
        planes_grouped
        .dropna(subset=["speed"])
        .sort_values("speed", ascending=False)
        .head(10)
    )

    # Round speeds to 2 decimals for a cleaner display
    top_planes["speed"] = top_planes["speed"].round(2)

    fig = px.bar(
        top_planes,
        x="model",
        y="speed",
        color="manufacturer",     # Color-code by manufacturer
        hover_data=["manufacturer", "speed"],  # Extra info on hover
        title="Top 10 Fastest Plane Models",
        labels={"model": "Plane Model", "speed": "Average Speed (mph)"},
        text="speed"  # Display speed value on each bar
    )


    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )
    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig)



#########################################################################################



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

def get_carrier_name(carrier):
    query = f'SELECT * FROM airlines'
    df = get_df_from_database(query)

    name = df[df['carrier'] == carrier]['name']
    
    return name

def flight_info(departure, arrival):
    query = f'SELECT origin,dest,dep_time,flight,year,month,day,carrier FROM flights'
    df = get_df_from_database(query)
    
    df = df[df['origin'] == get_faa(departure)]
    df = df[df['dest'] == get_faa(arrival)]
    
    return df

def get_other_airports():
    
    query = f'SELECT faa,name FROM airports'

    df = get_df_from_database(query)
    nyc_airports = part3.get_nyc_airports()

    # df = pd.concat([df1, df2]).drop_duplicates(keep=False)
    df = df[~df['name'].isin(nyc_airports)]

    return list(df['name'])

def flights_per_airline(airport):
    query = f'SELECT carrier,dest,origin FROM flights'
    query2 = f'SELECT carrier,name FROM airlines'
    df = get_df_from_database(query)
    df2 = get_df_from_database(query2)

    df = df[df['dest']== airport]
    
    st.dataframe(df)
    
    rtn_df = pd.DataFrame(columns=['carrier','name','num_flights'],index=None)

    airline_set = set(df['carrier'])
    for id in airline_set:
        num = df[df['carrier']==id].size
        name = df2[df2['carrier']==id]['name'].item()
        
        new_row = pd.DataFrame({'carrier': [id], 'name': [name], 'num_flights': [num]})
        rtn_df = pd.concat([rtn_df,new_row])
    
    rtn_df = rtn_df.reset_index(drop=True)

    return rtn_df

def in_usa(name=None,faa=None):
    if name is not None:
        query = f'SELECT name,tzone FROM airports'
        df = get_df_from_database(query)
        row = df[df['name'] == name]

    elif faa is not None:
        query = f'SELECT faa,tzone FROM airports'
        df = get_df_from_database(query)
        row = df[df['faa'] == faa]
    
    time_zone = row['tzone'].item()

    if time_zone[:7] != 'America':
        return False
    else:
        return True
    
def average_daily_flights(airport=None):
    query = f'SELECT month, day,origin FROM flights'
    df = get_df_from_database(query)

    if airport is not None:
        faa = get_faa(airport)
        df = df[df['origin'] == faa]

    total_days = df.groupby(['month', 'day']).ngroups  

    total_flights = len(df.index)

    daily_average = round(total_flights / total_days, 2)

    return daily_average

    
def average_monthly_flights(airport=None):
    query = f'SELECT month,origin FROM flights'
    df = get_df_from_database(query)

    if airport is not None:
        faa = get_faa(airport)
        df = df[df['origin'] == faa]

    months = set(df['month'])
    

    current_month = 1
    total_size = 0
    for i in months:
        df_month = df[df['month'] == current_month]
        total_size += len(df_month.index)
        current_month += 1

    average = round(total_size / len(months),2)
    return average

# def get_nyc_names():
#     nyc_lst = ['FOK','ISP','FRG','JFK','LGA','HPN','MGJ','SWF','BGM','ELM','ITH','JHW',
#                'DKK','BUF','IAG','ROC','SYC','RME','ALB','SCH','GFL','ART','LKP','SLK','PBG','MSS','OGS']
#     query = f'SELECT name, faa FROM airports'
#     df = get_df_from_database(query)

#     df = df[df['faa'].isin(nyc_lst)]
#     return list(df['name'])

def get_lat_lon(faa):
    query = f'SELECT faa,lat,lon FROM airports'
    df = get_df_from_database(query)

    airport = df[df['faa'] == faa]
    lat = airport['lat'].item()
    lon = airport['lon'].item()

    return lat,lon

def get_flight_path(row):
    origin = row[0]
    dest = row[1]

    fig = go.Figure()
    lat1, lon1 = get_lat_lon(origin)
    lat2, lon2 = get_lat_lon(dest)
    #Origin Marker
    
    fig.add_trace(go.Scattergeo(
            lon = [lon1],
            lat = [lat1],
            mode = 'markers',
            name=origin,
            marker=dict(color='blue'),
            showlegend=True
        ))

    #Destination Marker
    fig.add_trace(go.Scattergeo(
        lon = [lon2],
        lat = [lat2],
        mode = 'markers',
        name=dest,
        marker=dict(color='red'),
        showlegend=True
    ))

    #Line of Flight path
    fig.add_trace(go.Scattergeo(
        lon = [lon1, lon2],
        lat = [lat1, lat2],
        mode = 'lines',
        line=dict(color='green'),
        showlegend=False
    ))
    if in_usa(faa=dest):
        fig.update_layout(
                geo_scope='usa',
            )
    return fig

def fill_departure_time(name):
    faa = get_faa(name)
    query = f'SELECT dep_time, sched_dep_time, dep_delay FROM flights WHERE origin = "{faa}"'
    df = get_df_from_database(query)

    for _,row in df.iterrows():
        # If departure time is unknown, calculate based on scheduled departure time and delay time
        if pd.isna(row['dep_time']):
            if pd.isna(row['dep_delay']):
                row['dep_time'] = row['sched_dep_time']
                
            else:
                row['dep_time'] = row['sched_dep_time'] + row['dep_delay']

    return df

def get_daily_flight_info(month,day,faa=None):

    month = st.selectbox('Month',['January','Feburary','March','April','May','June','July','August','September','October','November','December'])
    day = st.text_input('Day')

    if faa is not None:
        query = f'SELECT * FROM flights WHERE month="{month}" and day="{day}" and origin="{faa}"'
    else:
        query = f'SELECT * FROM flights WHERE month="{month}" and day="{day}"'

    df = get_df_from_database(query)
    st.dataframe(df)


################ Departing Airports ################
################  time of day & Delays by departure airport ###############


def get_flight_delays(airport_faa, month, day):
    """Fetch departure flight delays for a given airport."""
    query = f"""
        SELECT dep_time, dep_delay, sched_dep_time
        FROM flights
        WHERE month = {month} AND day = {day} 
        AND origin = '{airport_faa}' 
        AND dep_delay IS NOT NULL
    """
    df = get_df_from_database(query)
    return df if 'dep_time' in df.columns else pd.DataFrame()


def get_weather_info(airport_faa, month, day):
    """Fetch weather info for a selected airport and date."""
    query = f"""
        SELECT temp, wind_speed, visib
        FROM weather
        WHERE month = {month} AND day = {day} AND origin = '{airport_faa}'
    """
    return get_df_from_database(query)

def display_delay_chart(df):
    """Display average delay as a function of time, handling missing data safely."""
    if 'dep_time' not in df.columns:
        st.warning("Flight data is missing 'dep_time'. Cannot display delay chart.")
        return

    df['hour'] = (df['dep_time'] // 100) % 24
    df_grouped = df.groupby('hour')['dep_delay'].mean().reset_index()

    st.subheader("Average Delay on Selected Date")
    fig = px.line(df_grouped, x='hour', y='dep_delay', markers=True, 
                  labels={'hour': 'Hour of Day', 'dep_delay': 'Average Delay (minutes)'})
    st.plotly_chart(fig)




def display_weather_info(selected_airport, month, day):
    """Fetches and displays weather info for a selected airport and date, rounding up values."""
    
    # Get weather data from the database
    query = f"""
        SELECT temp, wind_speed, visib
        FROM weather
        WHERE month = {month} AND day = {day} AND origin = '{selected_airport}'
    """
    weather_df = get_df_from_database(query)

    st.subheader("Weather on Selected Date")

    if not weather_df.empty:
        # Convert values to numeric (handling potential string values)
        weather_df = weather_df.apply(pd.to_numeric, errors='coerce')  # Converts non-numeric values to NaN

        # Handle NaN values safely: replace NaN with 0 (or another placeholder)
        temp_min = np.ceil(weather_df['temp'].min()) if not np.isnan(weather_df['temp'].min()) else 0
        temp_mean = np.ceil(weather_df['temp'].mean()) if not np.isnan(weather_df['temp'].mean()) else 0
        temp_max = np.ceil(weather_df['temp'].max()) if not np.isnan(weather_df['temp'].max()) else 0

        wind_min = np.ceil(weather_df['wind_speed'].min()) if not np.isnan(weather_df['wind_speed'].min()) else 0
        wind_mean = np.ceil(weather_df['wind_speed'].mean()) if not np.isnan(weather_df['wind_speed'].mean()) else 0
        wind_max = np.ceil(weather_df['wind_speed'].max()) if not np.isnan(weather_df['wind_speed'].max()) else 0

        vis_min = np.ceil(weather_df['visib'].min()) if not np.isnan(weather_df['visib'].min()) else 0
        vis_mean = np.ceil(weather_df['visib'].mean()) if not np.isnan(weather_df['visib'].mean()) else 0
        vis_max = np.ceil(weather_df['visib'].max()) if not np.isnan(weather_df['visib'].max()) else 0

        st.markdown(f"""
        **Temperature (°C):**  
        - Low: {int(temp_min)}, Avg: {int(temp_mean)}, High: {int(temp_max)}  

        **Wind Speed (km/h):**  
        - Low: {int(wind_min)}, Avg: {int(wind_mean)}, High: {int(wind_max)}  

        **Visibility (km):**  
        - Low: {int(vis_min)}, Avg: {int(vis_mean)}, High: {int(vis_max)}  
        """)
    else:
        st.text("No weather data available.")


def format_time(time_value):
# """Converts time from HHMM format to 'HH:MM'. Handles NaN values."""
    if pd.isna(time_value) or time_value is None:
        return "N/A"

    time_value = int(time_value)  # Ensure it's an integer
    hours = time_value // 100
    minutes = time_value % 100
    
    return f"{hours:02d}:{minutes:02d}"  # Ensure 2-digit format


def display_departure_times(df):
    """Displays scheduled and actual departure times in HH:MM format."""
    st.subheader("Departure Times")
    
    if not df.empty:
        # Extract scheduled and actual departure times
        sched_dep = format_time(df['sched_dep_time'].iloc[0]) if 'sched_dep_time' in df.columns else "N/A"
        actual_dep = format_time(df['dep_time'].iloc[0]) if 'dep_time' in df.columns else "N/A"
    else:
        sched_dep, actual_dep = "N/A", "N/A"

    st.markdown(f"""
    **Scheduled Departure:**  {sched_dep}  
    **Actual Departure:**  {actual_dep}  
    """)


def get_selected_date():
    """Returns the user-selected date as (month, day), or (None, None) if not selected."""
    selected_date = st.sidebar.date_input("Select a date")

    # If the user has not interacted with the date picker, return None
    if not selected_date:
        return None, None
    
    return selected_date.month, selected_date.day




def time_based_statistics():
    """Displays statistics for departure airports only."""
    st.header("Statistics as a Function of Time", divider='gray')

    selected_departure = st.session_state.get("fd_origin")

    if not selected_departure:
        st.warning("Please select a departure airport in the sidebar.")
        return

    # 🔹 Use the new function to get the selected date
    month, day = get_selected_date()

    departure_faa = get_faa(selected_departure)
    if departure_faa:
        st.subheader(f"Departure Statistics for {selected_departure}")
        df = get_flight_delays(departure_faa, month, day)

        if not df.empty:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                display_delay_chart(df)
            with col2:
                display_weather_info(departure_faa, month, day)
                display_departure_times(df)
        else:
            st.warning(f"No flight data available for {selected_departure} on {month}/{day}.")



##############   #################


def time_based_statistics():
    """Displays statistics for departure airports only."""
    st.header("Statistics as a Function of Time", divider='gray')

    selected_departure = st.session_state.get("fd_origin")

    if not selected_departure:
        st.warning("Please select a departure airport in the sidebar.")
        return

    selected_date = st.sidebar.date_input("Select a date", value=pd.to_datetime("2023-01-01"))
    month, day = selected_date.month, selected_date.day

    departure_faa = get_faa(selected_departure)
    if departure_faa:
        st.subheader(f"Departure Statistics for {selected_departure}")
        df = get_flight_delays(departure_faa, month, day)

        if not df.empty:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                display_delay_chart(df)
            with col2:
                display_weather_info(departure_faa, month, day)
                display_departure_times(df)
        else:
            st.warning(f"No flight data available for {selected_departure} on {selected_date}.")



################ Delay analysis ################


def get_flight_delays_multiple(airport_faa_list, month, day):
    """Fetches flight delays for multiple departure airports on a given date."""
    airport_faa_str = "', '".join(airport_faa_list)  # Format for SQL IN clause
    query = f"""
        SELECT origin, dep_time, dep_delay
        FROM flights
        WHERE month = {month} AND day = {day}
        AND origin IN ('{airport_faa_str}')
        AND dep_delay IS NOT NULL
    """
    df = get_df_from_database(query)
    
    if df.empty or 'dep_time' not in df.columns:
        return pd.DataFrame()  # Return an empty DataFrame if no data is found
    
    # Convert departure time to hours for aggregation
    df['hour'] = (df['dep_time'] // 100) % 24
    return df


def display_departure_delay_comparison():
    """Displays a line graph comparing departure delays for three major airports only after a date is selected."""
    st.subheader("Comparison of Departure Delays Across Airports")

    # 🔹 Check if the user has selected a date
    month, day = get_selected_date()

    if month is None or day is None:
        st.warning("Please select a departure date in the sidebar.")
        return  # Stop execution until the user selects a date


    # if not get_selected_date():
    #     st.warning("Please select a departure date in the sidebar.")
    #     return  # Stop execution until the user selects a date


    # if not selected_departure:
    #     st.warning("Please select a departure airport in the sidebar.")
    #     return



    # Define the three NYC airports
    nyc_airports_faa = ['JFK', 'LGA', 'EWR']  # FAA codes for JFK, LaGuardia, and Newark

    # Fetch delay data for all three airports
    df = get_flight_delays_multiple(nyc_airports_faa, month, day)

    if df.empty:
        st.warning(f"No flight delay data available for {month}/{day}.")
        return

    # Group by hour and airport, then compute the average delay
    df_grouped = df.groupby(['hour', 'origin'])['dep_delay'].mean().reset_index()

    # Plot using Plotly
    fig = px.line(df_grouped, x='hour', y='dep_delay', color='origin',
                  labels={'hour': 'Hour of Day', 'dep_delay': 'Average Delay (minutes)', 'origin': 'Airport'},
                  markers=True, title="Average Departure Delays Throughout the Day")

    st.plotly_chart(fig)











###############  ##############

def initialize_page():
    """Initializes the main dashboard page layout and displays general flight information."""
    
    # ✅ Ensure session state variables are initialized before use
    if "fd_details" not in st.session_state:
        st.session_state.fd_details = None
    if "fd_show_data" not in st.session_state:
        st.session_state.fd_show_data = False
    if "fd_start" not in st.session_state:
        st.session_state.fd_start = 0
    if "fd_origin" not in st.session_state:
        st.session_state.fd_origin = None
    if "fd_dest" not in st.session_state:
        st.session_state.fd_dest = None
    if "fetch_specific_info" not in st.session_state:
        st.session_state.fetch_specific_info = False
    if "fetch_general_info" not in st.session_state:
        st.session_state.fetch_general_info = True
    if "delay_info_ap" not in st.session_state:
        st.session_state.delay_info_ap = None
    if "map_type" not in st.session_state:
        st.session_state.map_type = "inter"
    if "map_airport_loc" not in st.session_state:
        st.session_state.map_airport_loc = None
    if "selected_airport" not in st.session_state:
        st.session_state.selected_airport = None


    # Load airports data
    query = 'SELECT faa, name, lat, lon, tzone FROM airports'
    all_airports_df = get_df_from_database(query)

    # Create Page Title
    st.title('Flight Information Dashboard')

    display_flight_statistics()  # Add statistics section
    display_airline_market_share() # show airline flights didtribution
    # Load airports data
    query = 'SELECT faa, name, lat, lon, tzone FROM airports'
    all_airports_df = get_df_from_database(query)

   

    # NYC Flight Info and Delays Section
    st.header('NYC Flight Info and Delays', divider='gray')

    if 'fetch_specific_info' not in st.session_state:
        st.session_state.fetch_specific_info = False
    if 'fetch_general_info' not in st.session_state:
        st.session_state.fetch_general_info = True
    if 'delay_info_ap' not in st.session_state:
        st.session_state.delay_info_ap = None

    # Buttons to select flight information type
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if st.button('All NYC Airports'):
                st.session_state.fetch_specific_info = False
                st.session_state.fetch_general_info = True
        with col2:
            if st.button('Select Airport'):
                st.session_state.fetch_specific_info = True
                st.session_state.fetch_general_info = False

        if st.session_state.fetch_specific_info:
            names = part3.get_nyc_airports()
            airport = st.selectbox('Select Departing Airport', names, index=None, placeholder='Enter airport name')
            if airport:
                st.session_state.delay_info_ap = airport
                st.text(f'Average Daily Flights: {average_daily_flights(airport)} flights')
                st.text(f'Average Monthly Flights: {average_monthly_flights(airport)} flights')

        if st.session_state.fetch_general_info:
            st.text(f'Average Daily Flights from NYC: {average_daily_flights()} flights')
            st.text(f'Average Monthly Flights from NYC: {average_monthly_flights()} flights')

    # Map of Airports Section
    st.header('Map of Airports', divider='gray')

    if 'map_type' not in st.session_state:
        st.session_state.map_type = 'inter'
    if 'map_airport_loc' not in st.session_state:
        st.session_state.map_airport_loc = None
    if 'selected_airport' not in st.session_state:
        st.session_state.selected_airport = None

    # Buttons to switch between US and International maps
    col1, col2 = st.columns(2)
    with col1:
        if st.button('United States'):
            st.session_state.map_type = 'usa'
            st.session_state.map_airport_loc = None
    with col2:
        if st.button('International'):
            st.session_state.map_type = 'inter'
            st.session_state.map_airport_loc = None

    # Determine which map to show
    if st.session_state.map_airport_loc is not None:
        fig = st.session_state.map_airport_loc
    elif st.session_state.map_type == 'inter':
        fig = part1.all_airports(all_airports_df)
    else:
        fig = part1.only_usa(all_airports_df)

    st.plotly_chart(fig, key='main_map')

    # Dropdown for selecting an airport location
    col3, col4 = st.columns([0.9, 0.1])
    with col3:
        selected = st.selectbox(
            'Find Location of Airport',
            all_airports_df['name'],
            index=None if st.session_state.selected_airport is None else all_airports_df['name'].tolist().index(st.session_state.selected_airport),
            placeholder='Enter airport name'
        )
        if selected:
            st.session_state.selected_airport = selected
            temp_df = all_airports_df[all_airports_df['name'] == selected]
            codes = temp_df['faa'].item()
            if in_usa(selected):
                st.session_state.map_airport_loc = part1.flight_paths([codes], temp_df)
            else:
                st.session_state.map_airport_loc = part1.flight_paths([codes], temp_df)

            st.plotly_chart(st.session_state.map_airport_loc)

    with col4:
        if st.button('Clear'):
            st.session_state.map_airport_loc = None
            st.session_state.selected_airport = None
            st.session_state.map_type = 'inter'
            st.plotly_chart(part1.all_airports(all_airports_df), key='reset_map')

    # Airport Specific Details Section
    st.header('Airport Specific Details', divider='gray')
    with st.container():
        name = st.selectbox('Airport Name', all_airports_df['name'], index=None, placeholder='Enter airport name')
        if name:
            id = all_airports_df[all_airports_df['name'] == name]
            temp_df = flights_per_airline(id['faa'].item())
            st.plotly_chart(px.pie(temp_df, names='name', values='num_flights'))

    # Airlines' Average Departure Delays Section
    st.header("Airlines' Average Departure Delays", divider='gray')
    delay_data = part3.average_departure_delay()
    st.bar_chart(delay_data, x_label='Airline', y_label='Average Departure Delay')

    # Flight Details Section
    st.header("Flight Details", divider='gray')
    with st.container():
        if st.session_state.fd_details is not None:
            row = st.session_state.fd_details
            origin, dest, dep_time, flight_num, year, month, day, carrier_code = row
            carrier = get_carrier_name(carrier_code)
            date = f'{month}/{day}/{year}'
            dep_hour = "{:02d}".format(int(dep_time // 100))
            dep_min = "{:02d}".format(int(dep_time % 100))

            st.subheader(f'Flight {flight_num} from {origin} to {dest}')
            fig = get_flight_path(row)
            st.plotly_chart(fig)
            st.text(f'Departure Time: {dep_hour}:{dep_min}')
            st.text(f'Date: {date}')
            st.text(f'Airline: {carrier}')
        else:
            st.text('Please enter flight details in sidebar. Additional flight info will appear here once details are entered.')



######### Sidebar #########

def create_sidebar():
    """Creates the sidebar UI for selecting departure and arrival airports and viewing flight details."""
    with st.sidebar:
        st.title('Find your flight:')
        
        # Dropdowns for departure and arrival airports
        departure = st.selectbox('Departure', nyc_airports, index=None, placeholder='Enter departing airport name')
        arrival = st.selectbox('Arrival', other_airports, index=None, placeholder='Enter arriving airport name')
        
        # Update session state to store the selected airport
        if departure:
            st.session_state["fd_origin"] = departure  # Store departure airport in session state
        
        if departure and arrival:
            flight_df = flight_info(departure, arrival)
            flight_df = flight_df.reset_index(drop=True)
            end = len(flight_df.index)
            
            if end > 0:
                if st.button('View Flight Info', icon='✈️'):
                    st.session_state.fd_show_data = True
                    st.session_state.fd_origin = get_faa(departure)
                    st.session_state.fd_dest = get_faa(arrival)
            else:
                st.text(f'No flights from {departure} to {arrival}. Please try again.')

            # Display flight details
            if st.session_state.fd_show_data:
                for i in range(min(10, end - st.session_state.fd_start)):
                    row = flight_df.iloc[i + st.session_state.fd_start]
                    
                    carrier = get_carrier_name(row['carrier'])
                    flight_num = row['flight'].item()
                    dep_time = row['dep_time']
                    dep_hour = "{:02d}".format(int(dep_time // 100))
                    dep_min = "{:02d}".format(int(dep_time % 100))
                    year, month, day = row['year'], row['month'], row['day']

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
                        with col1:
                            st.text('Date (MM/DD/YYYY):')
                            st.text(f'{month}/{day}/{year}')
                        with col2:
                            st.text('Flight Number:')
                            st.text(f'{flight_num}')
                        with col3:
                            if st.button('Details', key=i):
                                st.session_state.fd_details = row.tolist()
                                st.rerun()

                # Pagination buttons
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    if st.button('View Previous'):
                        if st.session_state.fd_start - 10 >= 0:
                            st.session_state.fd_start -= 10
                            st.rerun()
                with col2:
                    if st.button('View More'):
                        if st.session_state.fd_start + 10 < end:
                            st.session_state.fd_start += 10
                            st.rerun()

        else:
            st.session_state.fd_show_data = False
            st.session_state.fd_details = None



########### Main Function ###########

def main():
    """Main function to run the Streamlit app."""
    initialize_page()  # Sets up the main dashboard

    # Load airport data required for sidebar dropdowns
    global nyc_airports, other_airports
    nyc_airports = part3.get_nyc_airports()
    other_airports = get_other_airports()
    create_sidebar()   # Initializes the sidebar separately
    time_based_statistics()  # Displays time-based statistics
    display_departure_delay_comparison()  # Displays departure delay comparison
    display_flights_by_month()
    display_top_manufacturers_for_destination()
    display_plane_statistics()


if __name__ == '__main__':
    main()


