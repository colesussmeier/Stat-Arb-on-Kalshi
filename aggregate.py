import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def aggregate_flight_data():
    """
    Aggregate flight-related trends with TSA passenger data.
    Convert TSA daily data to weekly totals and merge with flight trends.
    """
    print("Loading flight-related trends data...")
    flight_trends = pd.read_csv('data/flight_related_trends_combined.csv')
    flight_trends['date'] = pd.to_datetime(flight_trends['date'])
    
    print("Loading TSA passenger data...")
    tsa_data = pd.read_csv('data/tsa_passenger_data.csv')
    tsa_data['date'] = pd.to_datetime(tsa_data['date'], format='%m/%d/%Y')
    
    print("Converting TSA daily data to weekly aggregates...")
    tsa_data = tsa_data.sort_values('date').reset_index(drop=True)

    tsa_data.set_index('date', inplace=True)

    # Resample to 7-day periods, summing only the passenger_volume column (aggregate to last day of week)
    tsa_weekly = tsa_data[['passenger_volume']].resample('7D', label='right', closed='right').sum()

    print(tsa_weekly.head(14))
    tsa_weekly.reset_index(inplace=True)

    tsa_weekly.rename(columns={
        'passenger_volume': 'weekly_passenger_volume'
    }, inplace=True)



    print("Merging datasets...")
    merged_data = pd.merge(
        flight_trends, 
        tsa_weekly, 
        on='date', 
        how='inner'
    )
    
    merged_data = merged_data.sort_values('date')
    
    print(f"Merged dataset contains {len(merged_data)} weeks of data")
    print(f"Date range: {merged_data['date'].min()} to {merged_data['date'].max()}")
    
    output_path = 'data/full_dataset.csv'
    merged_data.to_csv(output_path, index=False)
    print(f"Full dataset saved to {output_path}")
    
    return merged_data


if __name__ == "__main__":
    full_dataset = aggregate_flight_data()
