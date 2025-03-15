import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import part1
import part3


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
    
    return name.item()

def flight_info(departure, arrival):
    query = f'SELECT origin,dest,dep_time,flight,year,month,day,carrier FROM flights'
    df = get_df_from_database(query)
    
    df = df[df['origin'] == get_faa(departure)]
    df = df[df['dest'] == get_faa(arrival)]
    
    return df

def get_other_airports():
    
    query = f'SELECT * FROM airports'

    df1 = get_df_from_database(query)
    df2 = part3.get_nyc_airports()

    df = pd.concat([df1, df2]).drop_duplicates(keep=False)

    return df

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

def in_usa(name):
    query = f'SELECT name,tzone FROM airports'
    df = get_df_from_database(query)

    row = df[df['name'] == name]
    time_zone = row['tzone'].item()

    if time_zone[:7] != 'America':
        return False
    else:
        return True
    
def average_daily_flights():
    query = f'SELECT month, day FROM flights'
    df = get_df_from_database(query)

    total_days = df.groupby(['month', 'day']).ngroups  

    total_flights = len(df.index)

    daily_average = round(total_flights / total_days, 2)

    return daily_average
    
def average_monthly_flights():
    query = f'SELECT month FROM flights'
    df = get_df_from_database(query)

    months = set(df['month'])
    

    current_month = 1
    total_size = 0
    for i in months:
        df_month = df[df['month'] == current_month]
        total_size += len(df_month.index)
        current_month += 1

    average = round(total_size / len(months),2)
    return average



def initalize_page():
    st.set_page_config(layout='wide')
    flight_df = pd.DataFrame()

    query = f'SELECT faa,name,lat,lon,tzone FROM airports'
    all_airports_df = get_df_from_database(query)

    # Create Title
    st.title('Flight Information Dashboard')


    
    st.header('General Flight Info',divider='gray')
    
    #Daily Average Flights
    col1, col2 = st.columns(2)
    with col1:
        st.text('Average Daily Flights from NYC: ')
    with col2:
        st.text(f'{average_daily_flights()} flights')

    #Monthly Average Flights
    col1, col2 = st.columns(2)
    with col1:
        st.text('Average Monthly Flights from NYC: ')
    with col2:
        st.text(f'{average_monthly_flights()} flights')




    #Show Map of All Airports
    st.header('Map of Airports',divider='gray') #Header for section

    # Initialize session state for map type and selected airport location
    if 'map_type' not in st.session_state:
        st.session_state.map_type = 'inter'
    if 'map_airport_loc' not in st.session_state:
        st.session_state.map_airport_loc = None  
    if 'selected_airport' not in st.session_state:
        st.session_state.selected_airport = None 
        

    # Handle button clicks
    col1, col2 = st.columns(2)
    with col1:
        if st.button('United States'):
            st.session_state.map_type = 'usa'
            st.session_state.map_airport_loc = None  # Reset selected airport
    with col2:
        if st.button('International'):
            st.session_state.map_type = 'inter'
            st.session_state.map_airport_loc = None  # Reset selected airport

    # Generate the appropriate map
    if st.session_state.map_airport_loc is not None:
        fig = st.session_state.map_airport_loc  # Use selected airport map
    elif st.session_state.map_type == 'inter':
        fig = part1.all_airports(all_airports_df)
    else:
        fig = part1.only_usa(all_airports_df)

    map_plot = st.empty()
    map_plot.plotly_chart(fig, key='main_map')

    # Dropdown for selecting an airport
    col3, col4 = st.columns([.9,.1], vertical_alignment='bottom')
    with col3:
        selected = st.selectbox(
            'Find Location of Airport',
            all_airports_df['name'],
            index=None if st.session_state.selected_airport is None else all_airports_df['name'].tolist().index(st.session_state.selected_airport),
            placeholder='Enter name of desired airport'
        )
        if selected:
            st.session_state.selected_airport = selected
            temp_df = all_airports_df[all_airports_df['name'] == selected]
            codes = temp_df['faa'].item()
            if in_usa(selected):
                st.session_state.map_airport_loc = part1.flight_paths([codes],temp_df)
                #st.session_state.map_airport_loc = part1.only_usa(temp_df)
            else:
                st.session_state.map_airport_loc = part1.flight_paths([codes],temp_df)
                #st.session_state.map_airport_loc = part1.all_airports(temp_df)

            map_plot.plotly_chart(st.session_state.map_airport_loc)  # Update the map

    with col4:
        if st.button('Clear'):
            st.session_state.map_airport_loc = None
            st.session_state.selected_airport = None
            st.session_state.map_type = 'inter'
            map_plot.plotly_chart(part1.all_airports(all_airports_df), key='reset_map')  # Reset the map

    
    



        
        
        

    #Stats based on user input of airport
    st.header('Airport Specific Details',divider='gray')
    with st.container():
        name = st.selectbox('Airport Name',all_airports_df['name'],index=None,placeholder='Enter name of desired airport')
        if name:
            id = all_airports_df[all_airports_df['name'] == name]
            temp_df = flights_per_airline(id['faa'].item())
            st.plotly_chart(px.pie(temp_df,names='name',values='num_flights'))


    # Create Bar Graph
    with st.container():
        delay_data = part3.average_departure_delay()
        st.header("Airlines' Average Departure Delays",divider='gray')
        st.bar_chart(delay_data,x_label='Airline',y_label='Average Departure Delay')





    # Creates Sidebar
    flight_df = pd.DataFrame()
    nyc_airport_df = part3.get_nyc_airports()
    other_airport_df = get_other_airports()

    if 'fd_instruction' not in st.session_state:
        st.session_state.fd_instruction = 'Please enter flight details in sidebar. Additional flight info will appear here once inital details are entered.'
    if 'fd_data' not in st.session_state:
        st.session_state.fd_data = None
    if 'fd_start' not in st.session_state:
        st.session_state.fd_start = 0
    if 'fd_origin' not in st.session_state:
        st.session_state.fd_origin = None
    if 'fd_dest' not in st.session_state:
        st.session_state.fd_dest = None
    

    flight_details = st.container()
    with flight_details:
        st.header("Flight Details",divider='gray')
        if st.session_state.fd_instruction is not None:
            st.text(st.session_state.fd_instruction)
        if st.session_state.fd_data is not None:

            

            df = (st.session_state.fd_data)
            #st.dataframe(df)
            end = df.size

            x = f'Flights from {st.session_state.fd_origin} to {st.session_state.fd_dest}:'
            st.subheader(x)

            for i in range(10):
                row = df.loc[i+st.session_state.fd_start]

                carrier = get_carrier_name(row['carrier'])
                flight_num = row['flight']
                dep_time = row['dep_time']

                dep_hour = int(dep_time // 100)
                dep_hour = "{:02d}".format(dep_hour)
                dep_min = int(dep_time % 100)
                dep_min = "{:02d}".format(dep_min)

                year = row['year']
                month = row['month']
                day = row['day']

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.text(f'Date(MM/DD/YYYY): {month}/{day}/{year}')                        
                    with col2:
                        st.text(f'Flight Number: {flight_num}')
                    with col3:
                        st.text(f'Airline: {carrier}')
                    with col4:
                        st.text(f'Time of Departure: {dep_hour}:{dep_min}')

            col1, col2 = st.columns([.5,.5])
            with col1:
                if st.button('View Previous'):
                    start_num = st.session_state.fd_start
                    if start_num - 10 >= 0:
                        st.session_state.fd_start = start_num - 10
                        st.rerun()
            with col2:
                if st.button('View More'):
                    start_num = st.session_state.fd_start
                    if start_num + 10 < end:
                        st.session_state.fd_start = start_num + 10
                        st.rerun()
            

    with st.sidebar:
        st.title('Find your flight:')
        departure = st.selectbox('Departure',nyc_airport_df['name'],index=None,placeholder='Enter departing airport name')
        arrival = st.selectbox('Arrival',other_airport_df['name'],index=None,placeholder='Enter arriving airport name')
        if departure and arrival:
            flight_df = flight_info(departure,arrival)
            flight_df = flight_df.reset_index(drop=True)
            if flight_df.size > 0:
                if st.button('View Flight Info',icon='✈️'):
                    st.session_state.fd_instruction = None
                    st.session_state.fd_data = flight_df
                    st.session_state.fd_origin = get_faa(departure)
                    st.session_state.fd_dest = get_faa(arrival)
                    st.rerun()
                    
                    
                
            else:
                st.text(f'No flights from {departure} to {arrival}. Please try again.')


def main():
    initalize_page()

if __name__ == '__main__':
    main()