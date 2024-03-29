from tkinter import * 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
from plotly.subplots import make_subplots
import declarations
import F1_new_point_system
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2)

for _,row in F1_new_point_system.driverStandingsDF.iterrows():
    while len(row.loc[ "pointHistory"]) < len(declarations.grand_prix):
        row.loc[ "pointHistory"].append(row.loc[ "pointHistory"][-1])
    while len(row.loc[ "pointHistoryFIA"]) < len(declarations.grand_prix):
        row.loc[ "pointHistoryFIA"].append(row.loc[ "pointHistoryFIA"][-1])
    fig.add_trace( go.Scatter(x=declarations.grand_prix, y=row.loc[ "pointHistory"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)
    fig.add_trace( go.Scatter(x=declarations.grand_prix, y=row.loc[ "pointHistoryFIA"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)

for i, trace in enumerate(fig.data):
    if i == 0 or i % 2 == 0 :
        trace.name = f'New : {declarations.drivers[int(trace.text)]}'   # You can change this to any desired name
    else:
        trace.name = f'FIA : {declarations.drivers[int(trace.text)]}'


F1_new_point_system.ConstructorStandingsDF['teamId'] = F1_new_point_system.ConstructorStandingsDF['teamId'].map(declarations.teams)
fig.add_trace( go.Bar(x= F1_new_point_system.ConstructorStandingsDF["teamId"], y=F1_new_point_system.ConstructorStandingsDF[ "pointHistory"], text= "New point System") , row=1, col=2)
fig.add_trace( go.Bar(x= F1_new_point_system.ConstructorStandingsDF["teamId"], y=F1_new_point_system.ConstructorStandingsDF[ "pointHistoryFIA"], text= "FIA point System") , row=1, col=2)

fig.show()
