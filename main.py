import part1
import pandas as pd



def main():
    df = pd.read_csv('airports.csv')
    #part1.all_airports(df)
    lst = ['GRR','LAX','AAF','ABR']
    part1.create_histogram(df,lst)

if __name__ == '__main__':
    main()

