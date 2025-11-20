from tkinter import * 
from plotly.subplots import make_subplots
import declarations
import F1_new_point_system
import plotly.graph_objects as go
import numpy as np

driverStandingsDF, countries = F1_new_point_system.run(2024)
driverStandingsDF.to_csv("drivers.csv", index=False)

fig = make_subplots(rows=1, cols=1)
# adding the driver's traces to a graph plot
for _,row in driverStandingsDF.iterrows():
    #for the drivers that didn't score points, they are appointed with the same points they had till the previous race
    while len(row.loc[ "pointHistory"]) < len(countries):
        row.loc[ "pointHistory"].append(row.loc[ "pointHistory"][-1])
    while len(row.loc[ "pointHistoryFIA"]) < len(countries):
        row.loc[ "pointHistoryFIA"].append(row.loc[ "pointHistoryFIA"][-1])
    fig.add_trace( go.Scatter(x=countries, y=row.loc[ "pointHistory"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)
    fig.add_trace( go.Scatter(x=countries, y=row.loc[ "pointHistoryFIA"], 
                              mode="lines", text=row.loc["driverId"] ) , row=1, col=1)

# labels for drivers
for i, trace in enumerate(fig.data):
    # for each driver the first appearance it's with the new point system while the second is with the current
    if i == 0 or i % 2 == 0 :
        trace.name = f'New : {declarations.drivers[int(trace.text)]}'   
    else:
        trace.name = f'FIA : {declarations.drivers[int(trace.text)]}'

fig.update_layout(annotations=[])
options = [1, 2, 3]
results = {v:5 for v in options}

fig.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(label="New", method="update",
                     args=[{"visible": [True, False]}]),
                dict(label="Old", method="update",
                     args=[{"visible": [False, True]}]),
                dict(label="Both", method="update",
                     args=[{"visible": [True, True]}]),
            ],
            direction="down",
            x=1.1,          # position (x)
            y=1.1,            # position (y)
            xanchor="left",
            yanchor="top",
            showactive=True,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        ),
         dict(
            direction="down",
            x=0.1,
            y=1.15,
            showactive=True,
            buttons=[
                dict(
                    label=f"Value {gp}",
                    method="relayout",
                    args=[
                        {
                            "annotations": [
                                dict(
                                    x=0.1,
                                    y=600,
                                    text=f"Input: {gp}<b",
                                    showarrow=False,
                                    font=dict(size=18)
                                )
                            ]
                        }
                    ]
                )
                for gp in countries
            ]
        )
    ]
)

fig.show()
