import requests
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup

def prepare_data_for_simulation(driverStandingsDF, race_count):
    """
    Prepares the drivers' points history data for simulation by ensuring
    all drivers have point histories of equal length.

    Args:
        driverStandingsDF (pd.DataFrame): DataFrame containing driver standings with
            'pointHistory' and 'pointHistoryFIA' columns.
    """
    drivers_points = {}
    for _, row in driverStandingsDF.iterrows():
        cum_points = np.array(json.loads(row["pointHistory"]), dtype=int)
        per_race_points = np.diff(cum_points, prepend=0)  # first race = cum[0] - 0
        per_race_points = per_race_points[:race_count]
        drivers_points[row["driverId"]] = per_race_points.tolist()

    print(drivers_points)
    return drivers_points

def pad_all_histories(df, i, fill_if_empty=0):
    """
    Ensures that for every driver (row), pointHistory and pointHistoryFIA
    have length i (loop counter).
    """

    required_length = i + 1

    for row_index in df.index:
        for col in ["pointHistory", "pointHistoryFIA"]:

            lst = df.at[row_index, col]

            # Ensure it's a list (in case of NaN or other unexpected values)
            if not isinstance(lst, list):
                lst = [] if pd.isna(lst) else [lst]

            current_length = len(lst)

            if current_length < required_length:
                # Pad with last value or 0
                last_value = lst[-1]
                lst.extend([last_value] * (required_length - current_length))

            # Write back
            df.at[row_index, col] = lst


def missed_races(missed_racesDF, race, driverStandingsDF): 
    """ For each race, drivers that missed said race are appointed with the points they had up until the previous race
    Warning:
        might need adjusting for non main drivers that race again after they raced once

    Args: 
        driverStandingsDF : dataframe that includes the current points of each driver
        missed_racesDF    : dataframe that includes raceIds and the drivers that missed each race
        race              : race id
    
    Returns: 
        driverStandingsDF : the updated dataframe mentioned above 
    """
    for missing_driver in missed_racesDF._get_value(race,"driverId"):
        temp =  driverStandingsDF.loc[driverStandingsDF['driverId'] ==  missing_driver]
        row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  missing_driver ].index[0]
        driverStandingsDF.at[row_index, 'pointHistory'].append(driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1])
    return driverStandingsDF
  

def scrapping(url): 
    # Make a request to the webpage and parse the html content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing race results and extract the table rows
    table = soup.find('table', class_='Table-module_table__cKsW2')
    rows = table.find_all('tr')
    return rows

def get_deepest_text(tag):
    # If the tag has no children, return its text
    if not tag.find():
        return tag.get_text(strip=True)
    # Otherwise, go deeper
    return get_deepest_text(tag.find())
