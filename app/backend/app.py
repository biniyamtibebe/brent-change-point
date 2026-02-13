from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Import adfuller for stationarity test
from statsmodels.tsa.stattools import adfuller

# Add parent directory to path for src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from src.data_prep import load_oil_data, create_features, load_and_merge_events
    from src.models import BayesianChangePointDetector
    SRC_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import src modules: {e}")
    print("Running in API-only / sample mode")
    SRC_MODULES_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Global data
oil_df = None
events_df = None


def load_data():
    """Load processed data or fall back to sample data"""
    global oil_df, events_df

    prices_path = r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_oil_prices.csv'
    events_path = r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_events.csv'

    try:
        # Load prices with flexible column/index handling
        df = pd.read_csv(prices_path)
        date_col = next((c for c in ['date', 'Date', 'Unnamed: 0'] if c in df.columns), None)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df.set_index(date_col, inplace=True)
            df.index.name = 'date'
        oil_df = df

        # Load events
        events_df = pd.read_csv(events_path)
        events_df['date'] = pd.to_datetime(events_df['date'], errors='coerce')

        print("✓ Successfully loaded processed data")
        print(f"   Prices shape: {oil_df.shape} | Columns: {list(oil_df.columns)}")
        print(f"   Events: {len(events_df)}")

    except Exception as e:
        print(f"⚠ Could not load processed data: {e}")
        print("→ Falling back to rich sample data (2011-2022)")
        create_sample_data()


def create_sample_data():
    """Create rich sample data with full event analysis (used when real data is missing)"""
    global oil_df, events_df

    print("Creating rich sample dataset (2011–2022)...")

    # Generate realistic price series
    dates = pd.date_range(start='2011-01-01', end='2022-12-31', freq='B')
    np.random.seed(42)
    base = np.linspace(95, 65, len(dates)) + np.random.normal(0, 7, len(dates))
    prices = pd.Series(base, index=dates, name='price')

    # Features
    oil_df = pd.DataFrame({
        'price': prices,
        'log_price': np.log(prices),
        'log_returns': np.log(prices).diff().fillna(0),
        'rolling_std_30': np.log(prices).diff().fillna(0).rolling(30, min_periods=1).std()
    }, index=dates)

    # Rich events with description, reason, and impact analysis
    events_df = pd.DataFrame({
        'date': pd.to_datetime([
            '2011-02-20', '2020-03-11', '2021-03-23', '2022-02-24'
        ]),
        'description': [
            'Libya unrest intensifies – protests escalate ahead of civil war',
            'COVID-19 pandemic officially declared by WHO',
            'Suez Canal blocked by Ever Given container ship',
            'Russia launches full-scale invasion of Ukraine'
        ],
        'reason_for_price_change': [
            'Fear of major North African oil supply disruption during Arab Spring',
            'Global lockdowns cause unprecedented demand collapse',
            'Major oil shipping route blocked for nearly a week',
            'Western sanctions and fears of Russian oil supply cuts'
        ],
        'impact_analysis': [
            'Brent surged ~40% in Q1 2011 due to supply risk fears',
            'Historic crash — prices fell below $20/barrel in April 2020',
            'Short-term spike of 6–8% in March 2021',
            'Prices spiked above $130/barrel in March 2022 — highest since 2008'
        ],
        'category': ['Geopolitical', 'Economic', 'Logistics', 'Conflict']
    })

    print("✓ Rich sample data created (2011–2022)")
    print(f"   Prices: {oil_df.shape} | Events: {len(events_df)}")


# Load data on startup
load_data()


@app.route('/')
def index():
    return jsonify({
        "message": "Brent Oil Price Analysis API",
        "status": "running",
        "date_range": "2011-2022",
        "features": ["prices", "events", "change point detection", "statistical analysis"]
    })


@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Return price data for selected date range"""
    try:
        start = pd.to_datetime(request.args.get('start_date', '2011-01-01'))
        end = pd.to_datetime(request.args.get('end_date', '2022-12-31'))

        if oil_df is None:
            return jsonify({"error": "Data not loaded"}), 500

        filtered = oil_df[(oil_df.index >= start) & (oil_df.index <= end)].copy()

        # Find the raw price column (flexible)
        price_col = next((c for c in ['price', 'Price', 'Close', 'brent_price'] if c in filtered.columns), None)
        if not price_col and 'log_price' in filtered.columns:
            filtered['price'] = np.exp(filtered['log_price'])
            price_col = 'price'

        if not price_col:
            return jsonify({"error": "No price column found"}), 500

        data = [
            {
                'date': idx.strftime('%Y-%m-%d'),
                'price': float(row[price_col])
            }
            for idx, row in filtered.iterrows()
        ]

        return jsonify({
            "data": data,
            "count": len(data),
            "summary": {
                "min": float(filtered[price_col].min()),
                "max": float(filtered[price_col].max()),
                "avg": float(filtered[price_col].mean())
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """Return events with full analysis fields"""
    try:
        if events_df is None:
            return jsonify({"error": "No events loaded"}), 500

        events = []
        for _, r in events_df.iterrows():
            events.append({
                'date': r['date'].strftime('%Y-%m-%d'),
                'description': r.get('description', 'No description'),
                'reason_for_price_change': r.get('reason_for_price_change', 'No reason recorded'),
                'impact_analysis': r.get('impact_analysis', 'No analysis available'),
                'category': r.get('category', 'Unknown')
            })

        return jsonify({
            "events": events,
            "count": len(events)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Return basic and advanced statistical summary of the loaded data"""
    try:
        if oil_df is None:
            return jsonify({"error": "Data not loaded"}), 500

        stats = {
            "total_days": len(oil_df),
            "date_range": {
                "start": oil_df.index.min().strftime('%Y-%m-%d'),
                "end": oil_df.index.max().strftime('%Y-%m-%d')
            }
        }

        # Basic price stats (try multiple column names)
        price_col = next((c for c in ['price', 'Price', 'Close'] if c in oil_df.columns), None)
        if price_col:
            stats["price"] = {
                "min": float(oil_df[price_col].min()),
                "max": float(oil_df[price_col].max()),
                "mean": float(oil_df[price_col].mean()),
                "std": float(oil_df[price_col].std())
            }

        # Advanced returns statistics (your requested block)
        if 'log_returns' in oil_df.columns:
            returns = oil_df['log_returns'].dropna()
            if len(returns) > 10:
                stats["advanced"] = {
                    "annualized_volatility": float(returns.std() * np.sqrt(252) * 100),
                    "skewness": float(returns.skew()),
                    "kurtosis": float(returns.kurtosis()),
                    "adf_pvalue": float(adfuller(returns)[1])
                }
            else:
                stats["advanced"] = {"note": "Insufficient data for advanced statistics (need >10 returns)"}
        else:
            stats["advanced"] = {"note": "log_returns column not found"}

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# You can keep your other endpoints here (change-points, volatility, health, etc.)


if __name__ == '__main__':
    print("=" * 75)
    print("BRENT OIL PRICE ANALYSIS API")
    print("With advanced statistics (volatility, skewness, kurtosis, ADF test)")
    print("=" * 75)
    print("Server running on → http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
