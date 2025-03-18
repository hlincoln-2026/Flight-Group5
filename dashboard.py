import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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



def initalize_page():
    st.set_page_config(layout='wide')
    flight_df = pd.DataFrame()

    query = f'SELECT faa,name,lat,lon,tzone FROM airports'
    all_airports_df = get_df_from_database(query)

    # Create Title
    st.title('Flight Information Dashboard')

    
    st.header('NYC Flight Info and Delays',divider='gray')

    if 'fetch_specific_info' not in st.session_state:
        st.session_state.fetch_specific_info = False
    if 'fetch_general_info' not in st.session_state:
        st.session_state.fetch_general_info = True
    if 'delay_info_ap' not in st.session_state:
        st.session_state.delay_info_ap = None

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
            airport = st.selectbox('Select Departing Airport',names,index=None,placeholder='Enter name of desired airport')
            if airport:
                
                st.session_state.delay_info_ap = airport
                #Daily Average Flights
                st.text(f'Average Daily Flights: {average_daily_flights(airport)} flights')
                st.text(f'Average Monthly Flights: {average_monthly_flights(airport)}')
                # st.dataframe(fill_departure_time(airport))
                
                
            

        if st.session_state.fetch_general_info:
            #Daily Average Flights
            
            st.text(f'Average Daily Flights from NYC: {average_daily_flights()} flights')
            st.text(f'Average Monthly Flights from NYC: {average_monthly_flights()} flights')



    
    




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
    nyc_airports = part3.get_nyc_airports()
    other_airports = get_other_airports()


        
    if 'fd_show_data' not in st.session_state:
        st.session_state.fd_show_data = None
    if 'fd_start' not in st.session_state:
        st.session_state.fd_start = 0
    if 'fd_origin' not in st.session_state:
        st.session_state.fd_origin = None
    if 'fd_dest' not in st.session_state:
        st.session_state.fd_dest = None
    if 'fd_details' not in st.session_state:
        st.session_state.fd_details = None
    

    flight_details = st.container()
    with flight_details:
        st.header("Flight Details",divider='gray')
        
        if st.session_state.fd_details is not None:
            row = st.session_state.fd_details
            origin = row[0]
            dest = row[1]
            dep_time = row[2]
            flight_num = row[3]
            year = row[4]
            month = row[5]
            day = row[6]
            carrier = get_carrier_name(row[7])

            date = f'{month}/{day}/{year}'
            dep_hour = int(dep_time // 100)
            dep_hour = "{:02d}".format(dep_hour)
            dep_min = int(dep_time % 100)
            dep_min = "{:02d}".format(dep_min)

            st.subheader(f'Flight {flight_num} from {origin} to {dest}')
            fig = get_flight_path(row)
            st.plotly_chart(fig)
            st.text(f'Departure Time:  {dep_hour}:{dep_min}')
            st.text(f'Date: {date}')
            st.text(f'Airline: {carrier}')


            
        else:
            st.text('Please enter flight details in sidebar. Additional flight info will appear here once inital details are entered.')
            

    with st.sidebar:
        st.title('Find your flight:')
        departure = st.selectbox('Departure',nyc_airports,index=None,placeholder='Enter departing airport name')
        arrival = st.selectbox('Arrival',other_airports,index=None,placeholder='Enter arriving airport name')
        if departure and arrival:
            flight_df = flight_info(departure,arrival)
            flight_df = flight_df.reset_index(drop=True)
            end = flight_df.size
            if end > 0:
                if st.button('View Flight Info',icon='✈️'):
                    
                    st.session_state.fd_show_data = True
                    st.session_state.fd_origin = get_faa(departure)
                    st.session_state.fd_dest = get_faa(arrival)
                    
            else:
                st.text(f'No flights from {departure} to {arrival}. Please try again.')

            if st.session_state.fd_show_data:
                

                for i in range(10):
                    row = flight_df.loc[i+st.session_state.fd_start]

                    carrier = get_carrier_name(row['carrier'])
                    

                    flight_num = row['flight'].item()
                    dep_time = row['dep_time']

                    dep_hour = int(dep_time // 100)
                    dep_hour = "{:02d}".format(dep_hour)
                    dep_min = int(dep_time % 100)
                    dep_min = "{:02d}".format(dep_min)

                    year = row['year']
                    month = row['month']
                    day = row['day']

                    
                    

                    with st.container(border=True):
                        col1, col2,col3 = st.columns([0.4,0.3,0.3])
                        with col1:
                            st.text('Date(MM/DD/YYYY):')                  
                            st.text(f'{month}/{day}/{year}')      
                        with col2:
                            st.text('Flight Number:')
                            st.text(f'{flight_num}')
                        with col3:
                            if st.button('Details',key=i):
                                st.session_state.fd_details = row.tolist()
                                st.rerun()


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

        elif departure == None or arrival == None:
            st.session_state.fd_show_data = False
            st.session_state.fd_details = None
            


def main():
    initalize_page()

if __name__ == '__main__':
    main()