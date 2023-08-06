import os
import pandas as pd

# Get the path of the package directory
package_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(package_dir, "ISIN_sectors_ma.csv")
class ma_fi:

    def __init__(self):
        # Construct the path to the CSV file
        csv_path = os.path.join(package_dir, "ISIN_sectors_ma.csv")

        # List of available company names
        available_names = list(pd.read_csv(csv_path)["Instrument"])  # Add more company names here
