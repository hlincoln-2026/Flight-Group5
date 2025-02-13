import part1
import pandas as pd



def main():
    df = pd.read_csv('airports.csv')
    part1.all_airports(df)


if __name__ == '__main__':
    main()

