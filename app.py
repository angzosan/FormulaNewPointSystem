from tkinter import * 
from plotly.subplots import make_subplots
import declarations
import F1_new_point_system
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2)

# adding the driver's traces to a graph plot
for _,row in F1_new_point_system.driverStandingsDF.iterrows():
    #for the drivers that didn't score points, they are appointed with the same points they had till the previous race
    while len(row.loc[ "pointHistory"]) < len(declarations.grand_prix):
        row.loc[ "pointHistory"].append(row.loc[ "pointHistory"][-1])
    while len(row.loc[ "pointHistoryFIA"]) < len(declarations.grand_prix):
        row.loc[ "pointHistoryFIA"].append(row.loc[ "pointHistoryFIA"][-1])
    fig.add_trace( go.Scatter(x=declarations.grand_prix, y=row.loc[ "pointHistory"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)
    fig.add_trace( go.Scatter(x=declarations.grand_prix, y=row.loc[ "pointHistoryFIA"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)

# labels for drivers
for i, trace in enumerate(fig.data):
    # for each driver the first appearance it's with the new point system while the second is with the current
    if i == 0 or i % 2 == 0 :
        trace.name = f'New : {declarations.drivers[int(trace.text)]}'   
    else:
        trace.name = f'FIA : {declarations.drivers[int(trace.text)]}'

# adding the traces of the constructos to a bar plot
F1_new_point_system.ConstructorStandingsDF['teamId'] = F1_new_point_system.ConstructorStandingsDF['teamId'].map(declarations.teams)
fig.add_trace( go.Bar(x= F1_new_point_system.ConstructorStandingsDF["teamId"], y=F1_new_point_system.ConstructorStandingsDF[ "pointHistory"],    text= "New point System") , row=1, col=2)
fig.add_trace( go.Bar(x= F1_new_point_system.ConstructorStandingsDF["teamId"], y=F1_new_point_system.ConstructorStandingsDF[ "pointHistoryFIA"], text= "FIA point System") , row=1, col=2)

fig.show()
