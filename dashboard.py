import streamlit as st
import pandas as pd
import sqlite3
import part3


def get_faa(name):
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT faa,name FROM airports')

    df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])

    row = df.loc[df['name'] == name, 'faa'].item()
    return row

def distance_between_airports(departure, arrival):
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT origin,dest,distance,flight FROM flights')

    df = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])
    
    df = df[df['origin'] == get_faa(departure)]
    df = df[df['dest'] == get_faa(arrival)]
    
    return df

def get_other_airports():
    conn = sqlite3.connect('flights_database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM airports')

    df1 = pd.DataFrame(cursor.fetchall(), columns = [x[0] for x in cursor.description])
    df2 = part3.get_nyc_airports()

    df = pd.concat([df1, df2]).drop_duplicates(keep=False)

    return df

def flight_search():
    clicked = False
    nyc_airport_df = part3.get_nyc_airports()
    other_airport_df = get_other_airports()

    rtn_df = pd.DataFrame()

    st.title('Find your flight:')
    departure = st.selectbox('Departure',nyc_airport_df['name'],index=None,placeholder='Enter departing airport name')
    arrival = st.selectbox('Arrival',other_airport_df['name'],index=None,placeholder='Enter arriving airport name')
    if departure and arrival:
        rtn_df = distance_between_airports(departure,arrival)
        if rtn_df.size > 0:
            view_button = st.button('View Flight Info',icon='✈️')
            if view_button:
                clicked = True
            
        else:
            st.text(f'No flights from {departure} to {arrival}. Please try again.')

    
    rtn_df = rtn_df.reset_index(drop=True)

    return rtn_df, clicked


def initalize_page():
    clicked = False
    flight_df = pd.DataFrame()
    # Create Title
    st.title('Flight Information Dashboard')


    # Create Bar Graph
    with st.container():
        delay_data = part3.average_departure_delay()
        st.header("Airlines' Average Departure Delays",divider='gray')
        st.bar_chart(delay_data,x_label='Airline',y_label='Average Departure Delay')

    # Creates Sidebar
    with st.sidebar:
        flight_df, clicked = flight_search()

    with st.container(key='flight_details'):
        st.header("Flight Details",divider='gray')
        if clicked:
            st.dataframe(flight_df,use_container_width=True)
        

    


def main():
    initalize_page()


if __name__ == '__main__':
    main()