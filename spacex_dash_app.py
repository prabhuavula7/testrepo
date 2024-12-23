import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Check for unique launch sites and ensure data has been loaded correctly
print(spacex_df['LaunchSite'].unique())

# Create the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for selecting launch sites
    html.Br(),
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'Site 1', 'value': 'CCAFS_LC_40'},
                     {'label': 'Site 2', 'value': 'VAFB_SLC_4E'},
                     {'label': 'Site 3', 'value': 'KSC_LC_39A'},
                     {'label': 'Site 4', 'value': 'CCAFS_SLC_40'}
                 ],
                 value='ALL',  # Default value
                 placeholder="Select a Launch Site",
                 style={'width': '50%', 'padding': '3px'}
    ),
    
    # Pie chart for success/failure count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=spacex_df['Payload Mass (kg)'].min(),
        max=spacex_df['Payload Mass (kg)'].max(),
        step=1000,
        marks={0: '0', 5000: '5000', 10000: '10000', 15000: '15000'},
        value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
    ),
    
    # Scatter chart for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart based on site selection
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    # Debugging: Print selected site
    print(f"Selected Site: {selected_site}")
    
    if selected_site == 'ALL':
        # Check the group sizes
        data = spacex_df.groupby('class').size().reset_index(name='count')
    else:
        # Check if selected site exists in the data
        if selected_site not in spacex_df['LaunchSite'].values:
            print(f"Warning: {selected_site} not found in the data.")
            return px.pie()  # Return an empty chart if not found
        
        data = spacex_df[spacex_df['Launch Site'] == selected_site].groupby('class').size().reset_index(name='count')
    
    # Debugging: Print the data being used for the pie chart
    print(data)
    
    # Create the pie chart
    fig = px.pie(data, names='class', values='count', title=f'Success vs Failure for {selected_site}')
    return fig

# Callback for the scatter chart with payload vs success
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['LaunchSite'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class', title=f'Payload vs Launch Success for {selected_site}')
    return fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
