import pandas as pd
import numpy as np
from datetime import datetime
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_oil_data(filepath):
    """Load and preprocess Brent oil price data"""
    df = pd.read_csv(r"C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw\BrentOilPrices.csv")
    
    # Handle date parsing with multiple formats
    date_formats = ['%d-%b-%y', '%b %d, %Y', '%Y-%m-%d']
    
    for fmt in date_formats:
        try:
            df['Date'] = pd.to_datetime(df['Date'], format=fmt)
            break
        except ValueError:
            continue
    
    # If still not parsed, use pandas infer
    if df['Date'].dtype == 'object':
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Sort and set index
    df = df.sort_values('Date').set_index('Date')
    
    # Handle missing values
    df = df.interpolate(method='time')
    
    return df

def create_features(df, price_col='Price'):
    """Create additional features for analysis"""
    df = df.copy()
    
    # Log transformation
    df['log_price'] = np.log(df[price_col])
    
    # Returns
    df['returns'] = df[price_col].pct_change()
    df['log_returns'] = df['log_price'].diff()
    
    # Rolling statistics
    df['rolling_mean_30'] = df[price_col].rolling(window=30).mean()
    df['rolling_std_30'] = df['log_returns'].rolling(window=30).std()
    
    # Volatility clustering
    df['volatility_cluster'] = (df['log_returns'].abs() > 
                                df['log_returns'].abs().rolling(30).mean()).astype(int)
    
    return df

def load_and_merge_events(oil_df, events_path):
    """Merge event data with price data"""
    events_df = pd.read_csv(events_path)
    events_df['Date'] = pd.to_datetime(events_df['Date'])
    
    # Create a copy for merging
    merged_df = oil_df.copy()
    
    # Add event markers
    event_col = next((col for col in event.index if 'event' in col.lower() and 'desc' in col.lower()), 'Event_Description')
    merged_df.loc[closest_date, 'event_description'] = event[event_col]
    
    for _, event in events_df.iterrows():
        # Find closest trading day to event date
        closest_date = oil_df.index[oil_df.index.get_indexer([event['Date']], method='nearest')[0]]
        if closest_date in merged_df.index:
            merged_df.loc[closest_date, 'event'] = 1
            merged_df.loc[closest_date, 'event_description'] = event['Event_Description']
            merged_df.loc[closest_date, 'event_category'] = event['Category']
    
    return merged_df, events_df

def filter_time_period(df, start_date, end_date):
    """Filter data for specific time period"""
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df[mask]