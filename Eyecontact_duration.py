import time
from datetime import datetime
import json
import csv

with open("headposition_data.json", "r") as f:
    headposition_data = json.load(f)

current_date = datetime.now().strftime("%Y-%m-%d_%H:%M")
print("Current Time:", current_date)

print(headposition_data)

filename = f"data_{current_date}.csv"

with open(filename, "w", newline='') as csvfile:
    # Get the column names from the first item if it's a list of dictionaries
    if isinstance(headposition_data, list) and headposition_data:
        fieldnames = headposition_data[0].keys()  # Use keys of the first dict as column headers
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # Write the header row
        writer.writerows(headposition_data)  # Write all rows of data
    else:
        print("Data format not supported for CSV export")