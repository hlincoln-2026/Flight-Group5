import part1
import part3
import sqlite3
import pandas as pd



def main():
    df = pd.read_csv('airports.csv')

    #part1.all_airports(df)
    lst = ['GRR','LAX','AAF','ABR']
    part1.create_histogram(df,lst)
    
    connection = sqlite3.connect("flights_database.db")
    part3.verify_computed_distances(connection)

    connection.close()

if __name__ == '__main__':
    main()

