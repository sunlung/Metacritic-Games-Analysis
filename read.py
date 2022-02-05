
import pandas as pd
import csv

#def main():
     

    
    df = pd.read_csv('data.csv')
    df, df.columns = df[1:] , df.iloc[0]
    df['developers']=df['developers'].str[1:-1].str.split(r',(?!\S\)|\()')
    df['genres']=df['genres'].str[1:-1].str.split(r',(?!\S\)|\()')

    df.dtypes
#if __name__ == '__main__':
#    main()