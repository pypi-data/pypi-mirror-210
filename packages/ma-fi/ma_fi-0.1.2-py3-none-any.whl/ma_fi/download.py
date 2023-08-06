import os
import pandas as pd


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir,os.pardir)) #'C:\\Users\\Administrateur\\PycharmProjects\\mfinance'

package_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(package_dir, "ISIN_sectors_ma.csv")

# List of available company names
available_names = list(pd.read_csv(csv_path)["Instrument"])
def download(name, start_date, end_date, period):
    # Check if the name is valid
    if name not in available_names:
        print("Invalid company name.")
        return

    # Check if the start date is prior to the oldest available date
    oldest_date = pd.Timestamp('2018-05-16')
    if pd.Timestamp(start_date) < oldest_date:
        print("Start date cannot be prior to 2018-05-16.")
        return

    # Load data from CSV
    filename = f"{name}.csv"
    try:
        data = pd.read_csv(os.path.join(current_dir,"data_stocks",filename))

    except FileNotFoundError:
        print(f"Data not found for {name}.")
        return

    # Filter data based on start and end dates
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data = data[(data['Timestamp'] >= start_date) & (data['Timestamp'] <= end_date)]

    # Filter data based on period (currently only supports "1d")
    if period != "1d":
        print("Invalid period. Only '1d' is supported.")
        return

    # Print or return the resulting data
    return (data)  # Modify as per your requirement
