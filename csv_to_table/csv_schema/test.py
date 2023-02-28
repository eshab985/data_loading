import pandas as pd
import os

if __name__ == '__main__':
    csv_df = pd.read_csv('D:\\dev\\sample_files\\customer_details.csv')

    for row in csv_df:
        print(row)