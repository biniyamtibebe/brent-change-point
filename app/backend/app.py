from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Load data
oil_df = pd.read_csv(
    r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_oil_prices.csv',
    index_col='date',
    parse_dates=True
)

events_df = pd.read_csv(
    r'C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\processed_events.csv',
    parse_dates=['date']
)

# Ensure required columns exist
if 'log_returns' not in oil_df.columns:
    oil_df['log_returns'] = np.log(oil_df['price']).diff()

if 'rolling_std_30' not in oil_df.columns:
    oil_df['rolling_std_30'] = oil_df['log_returns'].rolling(30).std()


@app.route('/api/prices', methods=['GET'])
def get_prices():
    start_date = request.args.get('start_date', '2012-01-01')
    end_date = request.args.get('end_date', '2022-12-31')

    mask = (oil_df.index >= start_date) & (oil_df.index <= end_date)
    filtered_df = oil_df.loc[mask]

    prices = []
    for date, row in filtered_df.iterrows():
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': float(row['price']) if not pd.isna(row['price']) else 0,
            'log_returns': float(row['log_returns']) if not pd.isna(row['log_returns']) else 0,
            'rolling_volatility': float(row['rolling_std_30']) if not pd.isna(row['rolling_std_30']) else 0
        })

    return jsonify({
        'data': prices,
        'count': len(prices),
        'date_range': {'start': start_date, 'end': end_date}
    })


@app.route('/api/events', methods=['GET'])
def get_events():
    events = []
    for _, row in events_df.iterrows():
        events.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'description': row.get('event_description', ''),
            'category': row.get('event_category', '')
        })

    return jsonify({'events': events})


@app.route('/api/change-points', methods=['POST'])
def detect_change_points():
    from src.models import BayesianChangePointDetector

    data = request.json or {}
    start_date = data.get('start_date', '2012-01-01')
    end_date = data.get('end_date', '2022-12-31')

    mask = (oil_df.index >= start_date) & (oil_df.index <= end_date)
    filtered_df = oil_df.loc[mask]

    data_series = filtered_df['log_returns'].dropna().values
    dates = filtered_df['log_returns'].dropna().index

    detector = BayesianChangePointDetector(n_samples=2000, n_tune=500)

    # Removed invalid argument
    detector.fit(data_series)

    change_points = detector.get_change_points(dates)

    return jsonify({
        'change_points': {
            'mode_date': change_points['mode_date'].strftime('%Y-%m-%d'),
            'probability': float(change_points['probability'])
        }
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)