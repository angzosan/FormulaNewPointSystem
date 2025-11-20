import numpy as np
import pandas as pd
import utils
import declarations

def get_all_races_per_year(year:int):
    url = f'https://www.formula1.com/en/results/{year}/races'
    all_races_tr_tags = utils.scrapping(url)
    all_races_tr_tags = all_races_tr_tags[1:]
    url_race_map_array = []
    for race in all_races_tr_tags:
        url_race_map_array.append(strip_race(race))
    return url_race_map_array


def scrape(part):
    url ="https://www.formula1.com" + part
    return  utils.scrapping(url) 

def strip_race(race):
    race_data = race.find_all('td')
    for td in race_data:  # loop over each <td>
        a = td.find("a", href=True)  # find the single <a>
        if a:
            # Remove <svg> if present
            for svg in a.find("svg"):
                svg.decompose()
            
            link_info = {
                "url": a["href"],
                "country": a.get_text(strip=True)
            }
    return link_info

def strip(results):
    driver_data = results.find_all('td')
    elements = []
    for dd in driver_data:
        elements.append(dd.text.strip()) 
    return [elements[1], elements[3]] # [1, "Red Bull"]

def add_new_driver(new_points, fia_points, driverId, driverStandingsDF, race_index):
    new_system    = [ 0 for _ in range(race_index)]
    points_FIA = [ 0 for _ in range(race_index)]

    points_FIA.append(fia_points) 
    new_system.append(new_points)

    row = {
        "driverId"     : int(driverId),
        "pointHistory"    : new_system,   
        "pointHistoryFIA" : points_FIA
        }
    driverStandingsDF = pd.concat([driverStandingsDF, pd.DataFrame([row])], ignore_index=True)
    return driverStandingsDF

def append_points(results,fia_points,new_points, driverStandingsDF, race_index):

    single_data = strip(results)
    if int (single_data[0]) not in driverStandingsDF["driverId"].values : 
        driverStandingsDF = add_new_driver(new_points=new_points, fia_points=fia_points, driverId=single_data[0], driverStandingsDF=driverStandingsDF, race_index=race_index)
           
    else:
        #update dataframe row if driver is already in the dataframe
        row_index = driverStandingsDF.loc[driverStandingsDF['driverId'] == int(single_data[0])].index[0]
        driverStandingsDF.at[row_index, 'pointHistory'].append(new_points + driverStandingsDF.loc[row_index, "pointHistory"][-1])
        driverStandingsDF.at[row_index, 'pointHistoryFIA'].append(fia_points + driverStandingsDF.loc[row_index, "pointHistoryFIA"][-1]) 
    return driverStandingsDF  
        #constructors df update
      #  ConstructorStandingsDF.loc[team_index,'pointHistory']    = int (ConstructorStandingsDF.loc[team_index,'pointHistory']) + points
      #  ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'] = int (ConstructorStandingsDF.loc[team_index,'pointHistoryFIA'])  + int (single_data[7])


def run(year=2024):

    driverStandingsDF      = pd.DataFrame(declarations.driverStandings)
    url_race_map_array = get_all_races_per_year(year)
    countries = [item["country"] for item in url_race_map_array]

    for race_index, link_info in enumerate(url_race_map_array):
    
    # scrapping for the fastest lap
    # fastest_lap_times = scrape("fastest-laps")

    # fastest_lap_id = strip(fastest_lap_times[1])

        #scrapping for the overall race results
        race_results = scrape(link_info["url"])

        sprint = 0
        if countries[race_index] in declarations.sprint_weekends[year]:
            sprint_link = link_info["url"].replace('race-result', 'sprint-results')
            sprint_results = scrape(sprint_link)
            sprint = 1
            
        for i in range(1, len(race_results)): # for each driver
            sprint_fia_points = 0
            if sprint == 2: # Sprints are not working properly, sprint_results c=variable is never used, we currently assign the sprint points in accordance with race results
                sprint_fia_points = declarations.sprint_points[i-1]
            
            # Handle the actual grand prix
            fia_points = declarations.FIA_points[i-1]
            new_points = declarations.our_points[i-1]
            driverStandingsDF = append_points(race_results[i], fia_points +  sprint_fia_points, new_points + sprint_fia_points, driverStandingsDF=driverStandingsDF, race_index=race_index)      
        utils.pad_all_histories(driverStandingsDF, race_index)
    return driverStandingsDF, countries

if __name__ == "__main__":
    run()