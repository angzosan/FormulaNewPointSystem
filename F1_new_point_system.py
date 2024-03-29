import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
import declarations

def scrapping(url): 
    # Make a request to the webpage and parse the html content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing race results and extract the table rows
    table = soup.find('table', class_='resultsarchive-table')
    rows = table.find_all('tr')
    return rows


driverStandingsDF      = pd.DataFrame(declarations.driverStandings)
ConstructorStandingsDF = pd.DataFrame(declarations.ConstructorStandings)



for j in range(len(declarations.grand_prix)):
    
    url_fast_lap ="https://www.formula1.com/en/results.html/"+declarations.year+"/races/"+declarations.gp_code[j]+"/"+declarations.grand_prix[j]+"/fastest-laps.html"
    fastest_lap_times = scrapping(url_fast_lap) 

    fastest_lap_driver = fastest_lap_times[1].find_all('td')
    fastest_lap_id = [fld.text.strip() for fld in fastest_lap_driver]

    url_race ="https://www.formula1.com/en/results.html/"+declarations.year+"/races/"+declarations.gp_code[j]+"/"+declarations.grand_prix[j]+"/race-result.html"
    race_results = scrapping(url_race) 

    for i in range(1, len(race_results)):

        #retrieve the line regarding the drivers info
        driver_data = race_results[i].find_all('td')
        single_data = [dd.text.strip() for dd in driver_data]
        team_index = ConstructorStandingsDF.loc[ConstructorStandingsDF["teamId"] ==  declarations.drivers_teams[int (single_data[2])]  ].index[0]
    
        points = declarations.our_points[i-1]
        if ( int (fastest_lap_id[2]) == int (single_data[2]) and points > 0):
            points = points + 1
        if int (single_data[2]) not in driverStandingsDF["driverId"].values : 
            xFIA = []
            x =[]
            if j > 0 :
                x    = [ 0 for races in range(j)]
                xFIA = [ 0 for races in range(j)]
            xFIA.append(int (single_data[7]))
            x.append(points)

            #create data frame row if necessary - 
            row = {"driverId"        : int (single_data[2]),
                   "pointHistory"    : x,   
                   "pointHistoryFIA" : xFIA }
            driverStandingsDF = pd.concat([driverStandingsDF, pd.DataFrame([row])], ignore_index=True)
           
            ConstructorStandingsDF.loc[team_index,'pointHistory']    = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + points
            ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])

        else:

            #update dataframe row if driver is 
            row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  int (single_data[2]) ].index[0]

            driverStandingsDF.at[row_index, 'pointHistory'].append(points + driverStandingsDF.loc[row_index, "pointHistory"][-1]   )
            ConstructorStandingsDF.loc[team_index,'pointHistory'] = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + points

            driverStandingsDF.at[row_index, 'pointHistoryFIA'].append(int (single_data[7]) + driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1]  ) 
            ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])




    #special cases - TOFIX      
    if j == 1 :
        row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  55 ].index[0]
        driverStandingsDF.at[row_index, 'pointHistory'].append(driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1])
    if j == 2 :
        row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  2 ].index[0]
        driverStandingsDF.at[row_index, 'pointHistory'].append(driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1])





#ConstructorStandingsDF.to_csv(r"C:\\Users\\User\Desktop\\Constructors.csv", index=False)
#driverStandingsDF.to_csv(r"C:\\Users\\User\Desktop\\Drivers.csv", index=False)

#ConstructorStandingsDF.to_json(r'C:\\Users\\User\Desktop\\Constructors.json')
#driverStandingsDF.to_json(r'C:\\Users\\User\Desktop\\Drivers.json')

