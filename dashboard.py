#!/usr/bin/env python3
"""
Simple US 2-Year Futures Dashboard

A simple dashboard showing relative yield and key metrics.

Author: Aaryaman Saini
Date: 2025
"""

import dash
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load and process data
print("Loading data...")

df = pd.read_csv('us2y_futures.csv .csv')

# Clean column names
df.columns = df.columns.str.strip()
df = df.rename(columns={
    'Date': 'DateTime',
    'Lst Trd/Lst Px': 'LastTrd',
    'Decimal': 'DecimalPrice'
})

# Convert to datetime
df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Price'] = pd.to_numeric(df['DecimalPrice'], errors='coerce')
df['Yield'] = 100 - df['Price']
df['Time'] = df['DateTime'].dt.time
df['Date'] = df['DateTime'].dt.date

# Remove missing data
df = df.dropna(subset=['Price', 'Yield'])

# Filter for overnight sessions (18:00-08:00)
overnight_start = time(18, 0)
overnight_end = time(8, 0)

overnight_mask = (
    (df['Time'] >= overnight_start) | 
    (df['Time'] <= overnight_end)
)

processed_data = df[overnight_mask].copy()

# Create session groups
processed_data['SessionDate'] = processed_data['DateTime'].apply(
    lambda x: x.date() if x.time() >= overnight_start else x.date() - timedelta(days=1)
)

# Calculate relative yields
processed_data['RelativeYield'] = 0.0

for session_date in processed_data['SessionDate'].unique():
    session_mask = processed_data['SessionDate'] == session_date
    session_data = processed_data[session_mask].copy()
    
    if len(session_data) > 0:
        session_data = session_data.sort_values('DateTime')
        first_yield = session_data['Yield'].iloc[0]
        session_data['RelativeYield'] = session_data['Yield'] - first_yield
        processed_data.loc[session_mask, 'RelativeYield'] = session_data['RelativeYield'].values

print(f"Processed {len(processed_data)} data points")

# Calculate metrics
latest_data = df.sort_values('DateTime').iloc[-1]
current_yield = latest_data['Yield']
latest_date = latest_data['DateTime']

# Calculate 2s10s spread (approximate using data, simplified)
# Note: This is a placeholder - actual 2s10s requires 10-year treasury data
two_year_yield = current_yield
ten_year_yield = two_year_yield + 0.50  # Placeholder spread
two_ten_spread = ten_year_yield - two_year_yield

# Calculate 1-month volatility
month_ago = latest_date - pd.Timedelta(days=30)
recent_data = df[df['DateTime'] >= month_ago]
if len(recent_data) > 1:
    recent_data = recent_data.sort_values('DateTime')
    daily_yields = recent_data.groupby(recent_data['DateTime'].dt.date)['Yield'].last()
    if len(daily_yields) > 1:
        volatility = daily_yields.diff().std() * np.sqrt(252) * 100  # Annualized volatility in bps
    else:
        volatility = 0
else:
    volatility = 0

# Fed Funds Upper Bound (placeholder - should be fetched from actual data)
fed_funds_upper = 5.50  # Approximate current rate

# Create Dash app
app = dash.Dash(__name__)

# Create the relative yield chart
fig = go.Figure()

# Get unique sessions and sort
sessions = sorted(processed_data['SessionDate'].unique())[-6:]  # Get last 6 sessions
colors = px.colors.qualitative.Set1

for i, session in enumerate(sessions):
    session_data = processed_data[processed_data['SessionDate'] == session].sort_values('DateTime')
    
    # Format label for display
    display_date = session.strftime('%d-%b')
    
    fig.add_trace(go.Scatter(
        x=session_data['DateTime'],
        y=session_data['RelativeYield'],
        mode='lines',
        name=display_date,
        line=dict(color=colors[i % len(colors)], width=2.5),
        hovertemplate=f'<b>{display_date}</b><br>Time: %{{x}}<br>Relative Yield: %{{y:.4f}}<extra></extra>'
    ))

# Add average line
hourly_avg = processed_data.groupby(processed_data['DateTime'].dt.floor('H'))['RelativeYield'].mean()
fig.add_trace(go.Scatter(
    x=hourly_avg.index,
    y=hourly_avg.values,
    mode='lines',
    name='Avg',
    line=dict(color='black', width=2, dash='dash'),
    hovertemplate='<b>Avg</b><br>Time: %{x}<br>Relative Yield: %{y:.4f}<extra></extra>'
))

fig.update_layout(
    title={
        'text': 'TUZ5 Futures Yield (Relative)',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis=dict(
        title='Time',
        tickformat='%H:%M:%S',
        tickmode='linear',
        dtick=300000,  # 5 minutes in milliseconds
        tickangle=-45,  # Rotate labels to vertical
        gridcolor='#e0e0e0',
        showgrid=True
    ),
    yaxis=dict(
        title='Relative Yield',
        gridcolor='#e0e0e0',
        showgrid=True,
        zeroline=True,
        zerolinecolor='#b0b0b0'
    ),
    hovermode='x unified',
    template='plotly_white',
    height=500,
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=60, r=60, t=80, b=120)  # Increased bottom margin for rotated labels
)

# Define the layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("US 2-Year Futures Dashboard", 
               style={'textAlign': 'center', 'color': '#2c3e50', 
                     'margin': '20px 0', 'fontSize': '2em'}),
    ]),
    
    # Metrics Section
    html.Div([
        html.Div([
            html.Div([
                html.H3("Current 2-Year Yield", 
                       style={'margin': '0', 'color': '#2c3e50', 'fontSize': '0.9em'}),
                html.H2(f"{current_yield:.2f}%", 
                       style={'margin': '10px 0', 'color': '#3498db', 'fontSize': '2em'}),
                html.P(f"Latest: {latest_date.strftime('%Y-%m-%d %H:%M')}", 
                      style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.8em'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                     'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3("2s10s Spread", 
                       style={'margin': '0', 'color': '#2c3e50', 'fontSize': '0.9em'}),
                html.H2(f"{two_ten_spread:.2f}%", 
                       style={'margin': '10px 0', 'color': '#e74c3c', 'fontSize': '2em'}),
                html.P("Difference between 2-year and 10-year yields", 
                      style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.8em'})
            ], style={'flex': '1', 'marginLeft': '15px', 'padding': '20px', 'backgroundColor': 'white', 
                     'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3("1-Month Volatility", 
                       style={'margin': '0', 'color': '#2c3e50', 'fontSize': '0.9em'}),
                html.H2(f"{volatility:.2f} bps", 
                       style={'margin': '10px 0', 'color': '#27ae60', 'fontSize': '2em'}),
                html.P("Rolling σ of daily yield changes", 
                      style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.8em'})
            ], style={'flex': '1', 'marginLeft': '15px', 'padding': '20px', 'backgroundColor': 'white', 
                     'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3("Fed Funds Upper Bound", 
                       style={'margin': '0', 'color': '#2c3e50', 'fontSize': '0.9em'}),
                html.H2(f"{fed_funds_upper:.2f}%", 
                       style={'margin': '10px 0', 'color': '#9b59b6', 'fontSize': '2em'}),
                html.P("Current policy rate", 
                      style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '0.8em'})
            ], style={'flex': '1', 'marginLeft': '15px', 'padding': '20px', 'backgroundColor': 'white', 
                     'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'display': 'flex', 'gap': '15px', 'marginBottom': '30px'})
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px'}),
    
    # Chart Section
    html.Div([
        dcc.Graph(figure=fig)
    ], style={'padding': '0 20px', 'maxWidth': '1400px', 'margin': '0 auto'})
    
], style={'backgroundColor': '#f5f5f5', 'minHeight': '100vh', 'padding': '20px 0'})

if __name__ == "__main__":
    print("Starting dashboard on http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    app.run(debug=False, port=8050, host='127.0.0.1')

