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