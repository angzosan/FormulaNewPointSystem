import numpy as np
import pandas as pd
import utils
import declarations


def scrape(part):
    url ="https://www.formula1.com/en/results.html/"+declarations.YEAR+"/races/"+declarations.gp_code[race]+"/"+declarations.grand_prix[race]+"/"+ part +".html"
    return  utils.scrapping(url) 

def strip(results):
    driver_data = results.find_all('td')
    return [dd.text.strip() for dd in driver_data]


#initialize the data frames
missed_racesDF         = pd.DataFrame(declarations.missed_races)
driverStandingsDF      = pd.DataFrame(declarations.driverStandings)
ConstructorStandingsDF = pd.DataFrame(declarations.ConstructorStandings)

for race in range(len(declarations.grand_prix)):
    #scrapping for the fastest lap
    fastest_lap_times = scrape("fastest-laps")

    fastest_lap_id = strip(fastest_lap_times[1])

    #scrapping for the overall race results
    race_results = scrape( "race-result")

    sprint = 0
    if declarations.sprint_weekends[race] == 1:
        sprint_results = scrape("sprint-results")
        sprint = 1
        

    for i in range(1, len(race_results)):
        if sprint == 1 :
            single_data = strip(sprint_results[i])
            team_index  = ConstructorStandingsDF.loc[ConstructorStandingsDF["teamId"] ==  declarations.drivers_teams[int (single_data[2])]  ].index[0]

        
        #new driver case - add him in the df and set as 0 his result in all previous races
            if int (single_data[2]) not in driverStandingsDF["driverId"].values : 
                xFIA = []
                x =[]
                if race > 0 :
                    x    = [ 0 for races in range(race)]
                    xFIA = [ 0 for races in range(race)]
                xFIA.append(int (single_data[7]))
                x.append(int (single_data[7]))

            #create data frame row if necessary - 
                row = {"driverId"        : int (single_data[2]),
                   "pointHistory"    : x,   
                   "pointHistoryFIA" : xFIA }
                driverStandingsDF = pd.concat([driverStandingsDF, pd.DataFrame([row])], ignore_index=True)
           
            else:
            #update dataframe row if driver is already in the dataframe
                row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  int (single_data[2]) ].index[0]
                driverStandingsDF.at[row_index, 'pointHistory'].append(int (single_data[7]) + driverStandingsDF.loc[row_index, "pointHistory"][-1]   )
                driverStandingsDF.at[row_index, 'pointHistoryFIA'].append(int (single_data[7]) + driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1]  ) 
        
        #constructors df update
            ConstructorStandingsDF.loc[team_index,'pointHistory']    = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + int (single_data[7])
            ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])
    
    
        #retrieve the line regarding the drivers info
        single_data = strip(race_results[i])
        team_index  = ConstructorStandingsDF.loc[ConstructorStandingsDF["teamId"] ==  declarations.drivers_teams[int (single_data[2])]  ].index[0]

    
        #set the fastest lap point if the driver is within the new system's point range
        points = declarations.our_points[i-1]
        if ( int (fastest_lap_id[2]) == int (single_data[2]) and points > 0):
            points = points + 1
        
        #new driver case - add him in the df and set as 0 his result in all previous races
        if int (single_data[2]) not in driverStandingsDF["driverId"].values : 
            xFIA = []
            x =[]
            if race > 0 :
                x    = [ 0 for races in range(race)]
                xFIA = [ 0 for races in range(race)]
            xFIA.append(int (single_data[7]))
            x.append(points)

            #create data frame row if necessary - 
            row = {"driverId"        : int (single_data[2]),
                   "pointHistory"    : x,   
                   "pointHistoryFIA" : xFIA }
            driverStandingsDF = pd.concat([driverStandingsDF, pd.DataFrame([row])], ignore_index=True)
           
        else:
            #update dataframe row if driver is already in the dataframe
            row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] ==  int (single_data[2]) ].index[0]
            driverStandingsDF.at[row_index, 'pointHistory'].append(points + driverStandingsDF.loc[row_index, "pointHistory"][-1]   )
            driverStandingsDF.at[row_index, 'pointHistoryFIA'].append(int (single_data[7]) + driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1]  ) 
        
        #constructors df update
        ConstructorStandingsDF.loc[team_index,'pointHistory']    = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + points
        ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])
    
    driverStandingsDF = utils.missed_races(missed_racesDF, race, driverStandingsDF)   
