# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1(
                                        'SpaceX Launch Records Dashboard',
                                        style={
                                            'textAlign': 'center',
                                            'color': '#503D36',
                                            'font-size': 40
                                        }
                                ),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options= [{'label': 'All Sites', 'value': 'ALL'}] + [ {'label':site, 'value':site} for site in launch_sites ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks=dict( [(1000*i , 1000*i) for i in range(11)] ),
                                    value=[0, 10000]
                                    ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class', 
            names='Launch Site', 
            title='Total Launches with successful booster landing By Site'
            )
    else:
        # return the outcomes piechart for a selected site
        # Actually here filtered_df is a pd.Series not a pd.DataFrame
        filtered_df = spacex_df[ spacex_df['Launch Site'] == entered_site ].apply(lambda row : 'Success' if row['class']==1 else 'Failure',axis=1)
        fig = px.pie(
            filtered_df,
            values=filtered_df.value_counts().values,
            names=['Success','Failure'],
            title='Proportion of Launches with successful booster landing from Launch Site ' + entered_site
            )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value"))
def get_scatter(entered_site,slider_values):
    filtered_df = spacex_df[ (spacex_df['Payload Mass (kg)'] >= slider_values[0]) & (spacex_df['Payload Mass (kg)'] <= slider_values[1]) ]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class',
            color="Booster Version Category",
            title='Outcome (class=1 for successful booster landing, class=0 otherwise) of all Launches with Payload between {} kg and {} kg'.format(slider_values[0],slider_values[1])
            )
    else:
        # return the outcomes piechart for a selected site
        # Actually here filtered_df is a pd.Series not a Dataframe
        filtered_df = filtered_df[ filtered_df['Launch Site'] == entered_site ]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', 
            y='class',
            color="Booster Version Category",
            title='Outcome (class=1 for successful booster landing, class=0 otherwise) of all Launches from Site {} with Payload between {} kg and {} kg'.format(entered_site,slider_values[0],slider_values[1])
            )
    return fig

# Run the app
if (__name__ == '__main__'):
    app.run_server()
