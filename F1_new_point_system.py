import numpy as np
import pandas as pd
import utils
import declarations


def scrape(part):
    url ="https://www.formula1.com/en/results/"+declarations.YEAR+"/races/"+declarations.gp_code[race]+"/"+declarations.grand_prix[race]+"/"+ part
    return  utils.scrapping(url) 

def strip(results):
    driver_data = results.find_all('td')
    elements = []
    for dd in driver_data:
        elements.append(dd.text.strip()) 
    return [elements[1], elements[3]] # [1, "Red Bull"]

def add_new_driver(new_points, fia_points, driverId, driverStandingsDF):
    new_system    = [ 0 for _ in range(race)]
    points_FIA = [ 0 for _ in range(race)]

    points_FIA.append(fia_points) 
    new_system.append(new_points)

    row = {
        "driverId"     : int(driverId),
        "pointHistory"    : new_system,   
        "pointHistoryFIA" : points_FIA
        }
    driverStandingsDF = pd.concat([driverStandingsDF, pd.DataFrame([row])], ignore_index=True)
    return driverStandingsDF

def append_points(results,fia_points,new_points, driverStandingsDF):

    single_data = strip(results)
    if int (single_data[0]) not in driverStandingsDF["driverId"].values : 
        driverStandingsDF = add_new_driver(new_points=new_points, fia_points=fia_points, driverId=single_data[0], driverStandingsDF=driverStandingsDF)
           
    else:
        #update dataframe row if driver is already in the dataframe
        row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] == int(single_data[0])].index[0]
        driverStandingsDF.at[row_index, 'pointHistory'].append(new_points + driverStandingsDF.loc[row_index, "pointHistory"][-1])
        driverStandingsDF.at[row_index, 'pointHistoryFIA'].append(fia_points + driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1]) 
    return driverStandingsDF  
        #constructors df update
      #  ConstructorStandingsDF.loc[team_index,'pointHistory']    = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + points
      #  ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])

missed_racesDF         = pd.DataFrame(declarations.missed_races)
driverStandingsDF      = pd.DataFrame(declarations.driverStandings)
ConstructorStandingsDF = pd.DataFrame(declarations.ConstructorStandings)

for race in range(len(declarations.grand_prix)):
    #scrapping for the fastest lap
   # fastest_lap_times = scrape("fastest-laps")

  #  fastest_lap_id = strip(fastest_lap_times[1])

    #scrapping for the overall race results
    race_results = scrape("race-result")

    sprint = 0
    if declarations.sprint_weekends[race] == 1:
        sprint_results = scrape("sprint-results")
        sprint = 1
        
    for i in range(1, len(race_results)):
        if sprint == 1 :
            fia_points = declarations.sprint_points[i-1]
            new_points = declarations.sprint_points[i-1]
            driverStandingsDF = append_points(sprint_results[i], fia_points, new_points, driverStandingsDF=driverStandingsDF)
        
        # Handle the actual grand prix
        fia_points = declarations.FIA_points[i-1]
        new_points = declarations.our_points[i-1]
        driverStandingsDF = append_points(race_results[i], fia_points, new_points, driverStandingsDF=driverStandingsDF)
           
       # team_index  = ConstructorStandingsDF.loc[ConstructorStandingsDF["teamId"] ==  declarations.drivers_teams[int (single_data[1])]  ].index[0]

        #set the fastest lap point if the driver is within the new system's point range
       # if ( int (fastest_lap_id[2]) == int (single_data[2]) and points > 0):
        #    points = points + 1
        #         
    driverStandingsDF = utils.missed_races(missed_racesDF, race, driverStandingsDF)   
