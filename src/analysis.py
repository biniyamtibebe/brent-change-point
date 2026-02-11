import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_price_series(df, title="Brent Oil Prices Over Time"):
    """Plot raw price series with events"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Price Series', 'Log Returns'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Price series (use lowercase)
    if 'price' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price'),
            row=1, col=1
        )
    
    # Mark events if the column exists
    if 'event' in df.columns:
        event_dates = df[df['event'] == 1].index
        for date in event_dates:
            fig.add_vline(
                x=date, 
                line_width=1, 
                line_dash="dash", 
                line_color="red",
                row=1, col=1
            )
    
    # Log returns
    if 'log_returns' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['log_returns'], mode='lines', name='Log Returns'),
            row=2, col=1
        )
    
    fig.update_layout(height=600, title_text=title)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Log Returns", row=2, col=1)
    
    return fig

def test_stationarity(series):
    """Perform Augmented Dickey-Fuller test"""
    result = adfuller(series.dropna())
    return {
        'test_statistic': result[0],
        'p_value': result[1],
        'critical_values': result[4]
    }

def analyze_volatility(df, window=30):
    """Analyze volatility patterns"""
    if 'log_returns' not in df.columns:
        raise ValueError("Dataframe must have 'log_returns' column")
    
    volatility = df['log_returns'].rolling(window=window).std().dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=volatility.index, 
        y=volatility.values, 
        mode='lines',
        name=f'{window}-day Rolling Volatility'
    ))
    
    # Event markers
    if 'event' in df.columns:
        event_dates = df[df['event'] == 1].index
        for date in event_dates:
            if date in volatility.index:
                fig.add_vline(
                    x=date, 
                    line_width=1, 
                    line_dash="dash", 
                    line_color="red"
                )
    
    fig.update_layout(
        title=f'{window}-Day Rolling Volatility',
        xaxis_title='Date',
        yaxis_title='Volatility'
    )
    
    return fig, volatility

def event_impact_analysis(df, event_window=30):
    """Analyze price impact around events"""
    if 'event' not in df.columns:
        print("No 'event' column in dataframe. Returning empty DataFrame.")
        return pd.DataFrame()
    
    event_dates = df[df['event'] == 1].index
    impacts = []

    for event_date in event_dates:
        start_date = event_date - pd.Timedelta(days=event_window)
        end_date = event_date + pd.Timedelta(days=event_window)
        
        window_data = df.loc[start_date:end_date].copy()
        if len(window_data) > 10:
            pre_event = window_data[window_data.index < event_date]['price'].mean()
            post_event = window_data[window_data.index > event_date]['price'].mean()
            pct_change = ((post_event - pre_event) / pre_event) * 100
            
            impacts.append({
                'date': event_date,
                'pre_event_mean': pre_event,
                'post_event_mean': post_event,
                'pct_change': pct_change,
                'description': df.loc[event_date, 'event_description'] if 'event_description' in df.columns else "",
                'category': df.loc[event_date, 'event_category'] if 'event_category' in df.columns else ""
            })
    
    return pd.DataFrame(impacts)


