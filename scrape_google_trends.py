import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
import time
import os

def setup_pytrends():
    """Initialize pytrends connection"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        print("Successfully connected to Google Trends")
        return pytrends
        
    except Exception as e:
        raise Exception(f"Failed to connect to Google Trends: {e}")

def get_trends_data(pytrends, keywords, timeframe, category=0, geo='US', max_retries=3):
    """Get trends data for specified keywords with retry logic for rate limiting"""
    for attempt in range(max_retries):
        try:
            pytrends.build_payload(
                kw_list=keywords,
                cat=category,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            data = pytrends.interest_over_time()
            
            if not data.empty:
                # Remove the 'isPartial' column if it exists
                if 'isPartial' in data.columns:
                    data = data.drop(columns=['isPartial'])
                
                print(f"Successfully retrieved data for: {', '.join(keywords)}")
                return data
            else:
                print(f"No data found for keywords: {', '.join(keywords)}")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                # Rate limiting - use exponential backoff
                wait_time = (2 ** attempt) * 30  # 30, 60, 120 seconds
                if attempt < max_retries - 1:
                    print(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Rate limited after {max_retries} attempts. Skipping {keywords}")
                    return None
            else:
                print(f"Error retrieving data for {keywords}: {e}")
                return None
    
    return None

def save_data_to_csv(data, filename):
    """Save DataFrame to CSV file"""
    try:
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        data.to_csv(filepath)
        print(f"Data saved to: {filepath}")
        
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")

def main():
    """Main function to scrape Google Trends data for flight-related queries"""
    
    print("Starting Google Trends data collection for flight-related queries...")
    print("=" * 60)
    
    pytrends = setup_pytrends()
    if not pytrends:
        print("Failed to initialize pytrends. Exiting.")
        return
    
    # Define date range (from 2023 to today)
    start_date = "2023-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    timeframe = f"{start_date} {end_date}"
    
    print(f"Collecting data from {start_date} to {end_date}")
    print("=" * 60)
    
    queries = [
        {
            'keywords': ['flight status'],
            'category': 0,  # All categories
            'filename': 'flight_status_trends.csv',
            'description': 'Flight Status trends'
        },
        {
            'keywords': ['airport parking'],
            'category': 0,  # All categories  
            'filename': 'airport_parking_trends.csv',
            'description': 'Airport Parking trends'
        },
        {
            'keywords': ['car rental'],
            'category': 203,  # Air travel category
            'filename': 'car_rental_travel_trends.csv',
            'description': 'Car Rental trends (Travel category)'
        }
    ]
    
    all_data = {}
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Collecting {query['description']}...")
        
        data = get_trends_data(
            pytrends=pytrends,
            keywords=query['keywords'],
            timeframe=timeframe,
            category=query['category'],
            geo='US'
        )
        
        if data is not None:
            save_data_to_csv(data, query['filename'])
            all_data[query['keywords'][0]] = data
            
            print(f"   - Data shape: {data.shape}")
            print(f"   - Date range: {data.index.min()} to {data.index.max()}")
        
        # Add delay between queries to avoid rate limiting
        if i < len(queries):
            print("   - Waiting 10 seconds before next query...")
            time.sleep(10)
    

    if all_data:
        print(f"\n{'='*60}")
        print("Creating combined dataset...")
        
        combined_data = pd.DataFrame()
        
        for keyword, data in all_data.items():
            if not data.empty:
                column_name = keyword.replace(' ', '_')
                combined_data[column_name] = data.iloc[:, 0]
        
        if not combined_data.empty:
            combined_data.index = list(all_data.values())[0].index
            
            save_data_to_csv(combined_data, 'flight_related_trends_combined.csv')
            
            print(f"Combined data shape: {combined_data.shape}")
            print(f"Keywords included: {list(combined_data.columns)}")
    
    print(f"\n{'='*60}")
    print("Data collection completed!")

if __name__ == "__main__":
    main()
