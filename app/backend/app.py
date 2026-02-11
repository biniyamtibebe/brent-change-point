from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path to import src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from src.data_prep import load_oil_data, create_features, load_and_merge_events, filter_time_period
    from src.models import BayesianChangePointDetector
    DATA_LOADED = True
except ImportError as e:
    print(f"Warning: Could not import src modules: {e}")
    print("Running in API-only mode (data will be loaded from CSV files)")
    DATA_LOADED = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global data variables
oil_df = None
events_df = None

def load_data():
    """Load data on startup"""
    global oil_df, events_df
    
    try:
        # Load data
        oil_df = pd.read_csv('../../data/processed_oil_prices.csv', 
                           index_col='Date', parse_dates=True)
        events_df = pd.read_csv('../../data/processed_events.csv', 
                              parse_dates=['Date'])
        print("✓ Data loaded successfully")
        print(f"  Price data shape: {oil_df.shape}")
        print(f"  Events count: {len(events_df)}")
        
    except FileNotFoundError:
        print("⚠ Processed data not found. Creating from raw data...")
        try:
            # Try to create processed data
            oil_df = load_oil_data(r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw\BrentOilPrices.csv')
            oil_df = create_features(oil_df)
            oil_df, events_df = load_and_merge_events(oil_df, r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw\events.csv')
            
            # Save processed data
            os.makedirs(r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data', exist_ok=True)
            oil_df.to_csv(r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_oil_prices.csv')
            events_df.to_csv(r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_events.csv', index=False)
            print("✓ data processed and saved")
            
        except Exception as e:
            print(f"✗ Error processing data: {e}")
            # Create sample data for demo
            create_sample_data()

def create_sample_data():
    """Create sample data for demo purposes"""
    global oil_df, events_df
    
    print("Creating sample data for demo...")
    
    # Sample price data
    dates = pd.date_range('2020-01-01', '2022-12-31', freq='D')
    np.random.seed(42)
    
    # Create trending data with volatility
    base_trend = np.linspace(40, 100, len(dates))
    noise = np.random.normal(0, 5, len(dates))
    prices = base_trend + noise
    
    oil_df = pd.DataFrame({
        'date': dates,
        'price': prices,
        'log_price': np.log(prices),
        'log_returns': np.log(prices).diff(),
        'rolling_std_30': pd.Series(np.log(prices).diff()).rolling(30).std()
    })
    oil_df.set_index('date', inplace=True)
    
    # Sample events
    events_data = {
        'date': pd.to_datetime(['2020-03-11', '2021-03-23', '2022-02-24']),
        'event_description': [
            'COVID-19 pandemic declared',
            'Suez Canal blockage',
            'Russia invades Ukraine'
        ],
        'category': ['Economic', 'Logistics', 'Conflict']
    }
    events_df = pd.DataFrame(events_data)
    
    print("✓ Sample data created")

# Load data on startup
load_data()

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'message': 'Brent Oil Price Analysis API',
        'version': '1.0.0',
        'endpoints': {
            '/api/prices': 'GET - Get price data',
            '/api/events': 'GET - Get events data',
            '/api/change-points': 'POST - Detect change points',
            '/api/statistics': 'GET - Get statistics',
            '/api/volatility': 'GET - Get volatility metrics'
        },
        'status': 'running'
    })

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get price data for specific date range"""
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2022-12-31')
        
        if oil_df is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        mask = (oil_df.index >= start_date) & (oil_df.index <= end_date)
        filtered_df = oil_df[mask]
        
        # Convert to list for JSON
        prices = []
        for date, row in filtered_df.iterrows():
            price_item = {
                'date': date.strftime('%Y-%m-%d'),
                'price': float(row['Price']) if 'Price' in row else 0,
            }
            
            # Add additional fields if available
            if 'log_price' in row:
                price_item['log_price'] = float(row['log_price'])
            if 'log_returns' in row:
                price_item['log_returns'] = float(row['log_returns']) if not pd.isna(row['log_returns']) else 0
            if 'rolling_std_30' in row:
                price_item['rolling_volatility'] = float(row['rolling_std_30']) if not pd.isna(row['rolling_std_30']) else 0
            
            prices.append(price_item)
        
        return jsonify({
            'data': prices,
            'count': len(prices),
            'date_range': {'start': start_date, 'end': end_date},
            'summary': {
                'min_price': float(filtered_df['Price'].min()) if 'Price' in filtered_df else 0,
                'max_price': float(filtered_df['Price'].max()) if 'Price' in filtered_df else 0,
                'avg_price': float(filtered_df['Price'].mean()) if 'Price' in filtered_df else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        if events_df is None:
            return jsonify({'error': 'Events data not loaded'}), 500
        
        events = []
        for _, row in events_df.iterrows():
            events.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'description': row['Event_Description'],
                'category': row['Category']
            })
        
        # Group by category for statistics
        categories = events_df['Category'].value_counts().to_dict()
        
        return jsonify({
            'events': events,
            'count': len(events),
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-points', methods=['POST'])
def detect_change_points():
    """Detect change points using Bayesian method"""
    try:
        data = request.json
        start_date = data.get('start_date', '2020-01-01')
        end_date = data.get('end_date', '2022-12-31')
        
        if oil_df is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        # Filter data
        mask = (oil_df.index >= start_date) & (oil_df.index <= end_date)
        filtered_df = oil_df[mask]
        
        if len(filtered_df) < 100:
            return jsonify({'error': 'Insufficient data points (need at least 100)'}), 400
        
        # Use log returns if available, otherwise use price
        if 'log_returns' in filtered_df.columns:
            data_series = filtered_df['log_returns'].dropna().values
            data_type = 'log_returns'
        else:
            data_series = filtered_df['Price'].dropna().values
            data_type = 'price'
        
        dates = filtered_df.dropna().index
        
        # Detect change points
        detector = BayesianChangePointDetector(n_samples=1000, n_tune=500)
        detector.fit(data_series, n_change_points=1)
        
        change_points = detector.get_change_points(dates)
        
        if not change_points:
            return jsonify({'error': 'No change points detected'}), 404
        
        # Calculate statistics before/after change point
        if change_points['mode_date']:
            cp_index = np.where(dates == change_points['mode_date'])[0]
            if len(cp_index) > 0:
                cp_idx = cp_index[0]
                mean_before = np.mean(data_series[:cp_idx]) if cp_idx > 0 else 0
                mean_after = np.mean(data_series[cp_idx:]) if cp_idx < len(data_series) else 0
                pct_change = ((mean_after - mean_before) / abs(mean_before)) * 100 if mean_before != 0 else 0
            else:
                mean_before = mean_after = pct_change = 0
        else:
            mean_before = mean_after = pct_change = 0
        
        return jsonify({
            'change_points': {
                'mode_date': change_points['mode_date'].strftime('%Y-%m-%d') if change_points['mode_date'] else None,
                'probability': float(change_points.get('mode_probability', 0)),
                'mean_index': float(change_points.get('mean_index', 0)),
                'std_index': float(change_points.get('std_index', 0)),
                'data_type': data_type
            },
            'impact': {
                'mean_before': float(mean_before),
                'mean_after': float(mean_after),
                'pct_change': float(pct_change)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    try:
        if oil_df is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        # Basic statistics
        stats = {
            'total_days': len(oil_df),
            'date_range': {
                'start': oil_df.index[0].strftime('%Y-%m-%d'),
                'end': oil_df.index[-1].strftime('%Y-%m-%d')
            }
        }
        
        if 'Price' in oil_df.columns:
            stats['price'] = {
                'min': float(oil_df['Price'].min()),
                'max': float(oil_df['Price'].max()),
                'mean': float(oil_df['Price'].mean()),
                'std': float(oil_df['Price'].std())
            }
        
        if 'log_returns' in oil_df.columns:
            returns = oil_df['log_returns'].dropna()
            if len(returns) > 0:
                stats['returns'] = {
                    'mean': float(returns.mean()),
                    'std': float(returns.std()),
                    'skewness': float(returns.skew()),
                    'kurtosis': float(returns.kurtosis())
                }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    """Get volatility metrics"""
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2022-12-31')
        window = int(request.args.get('window', 30))
        
        if oil_df is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        mask = (oil_df.index >= start_date) & (oil_df.index <= end_date)
        filtered_df = oil_df[mask]
        
        if 'log_returns' not in filtered_df.columns:
            return jsonify({'error': 'Log returns not available'}), 400
        
        returns = filtered_df['log_returns'].dropna()
        
        if len(returns) < window:
            return jsonify({'error': f'Insufficient data for {window}-day window'}), 400
        
        # Calculate rolling volatility
        rolling_vol = returns.rolling(window=window).std()
        
        # Prepare response
        volatility_data = []
        for date, vol in rolling_vol.items():
            if not pd.isna(vol):
                volatility_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'volatility': float(vol)
                })
        
        return jsonify({
            'data': volatility_data,
            'window': window,
            'summary': {
                'mean_volatility': float(rolling_vol.mean()),
                'max_volatility': float(rolling_vol.max()),
                'min_volatility': float(rolling_vol.min()),
                'current_volatility': float(rolling_vol.iloc[-1]) if len(rolling_vol) > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': oil_df is not None,
        'events_loaded': events_df is not None
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Brent Oil Price Analysis API")
    print("=" * 60)
    print(f"Server running on: http://127.0.0.1:5000")
    print(f"API Documentation: http://127.0.0.1:5000/")
    print("\nAvailable endpoints:")
    print("  GET  /api/prices?start_date=...&end_date=...")
    print("  GET  /api/events")
    print("  POST /api/change-points")
    print("  GET  /api/statistics")
    print("  GET  /api/volatility?window=30")
    print("  GET  /api/health")
    print("\nPress CTRL+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)