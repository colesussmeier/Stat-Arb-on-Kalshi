import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
import time

def scrape_tsa_passenger_data():
    """Scrape passenger volume data from the TSA website"""
    
    urls = ["https://www.tsa.gov/travel/passenger-volumes",
            "https://www.tsa.gov/travel/passenger-volumes/2024",
            "https://www.tsa.gov/travel/passenger-volumes/2023"]
    
    # Set up headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    all_passenger_data = []
    
    for url in urls:
        print(f"Fetching data from {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the tbody tag containing the passenger data
            tbody = soup.find('tbody')
            
            if not tbody:
                print(f"Could not find <tbody> tag in {url}")
                continue
            
            rows = tbody.find_all('tr')
            page_data_count = 0
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 2:
                    date_text = cells[0].get_text(strip=True)
                    volume_text = cells[1].get_text(strip=True)
                    
                    if not date_text or not volume_text or 'Date' in date_text or 'Numbers' in volume_text:
                        continue
                    
                    try:
                        # Clean and parse the volume (remove commas, convert to int)
                        volume_clean = volume_text.replace(',', '').replace(' ', '')
                        volume = int(volume_clean)
                        
                        date_obj = datetime.strptime(date_text, '%m/%d/%Y')
                        
                        record = {
                            'date': date_obj,
                            'passenger_volume': volume
                        }
                        
                        all_passenger_data.append(record)
                        page_data_count += 1
                        
                    except (ValueError, IndexError) as e:
                        continue

            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue
    
    all_passenger_data.sort(key=lambda x: x['date'])
    
    return all_passenger_data

def save_data(data):
    """Save data in CSV format"""
    
    if not data:
        print("No data to save")
        return
    
    with open('data/tsa_passenger_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'passenger_volume'])  # Header row
        
        for record in data:
            date_str = record['date'].strftime('%m/%d/%Y')
            writer.writerow([date_str, record['passenger_volume']])
    
    print(f"Saved {len(data)} records to tsa_passenger_data.csv")

if __name__ == "__main__":
    print("TSA Passenger Volume Data Scraper")
    
    data = scrape_tsa_passenger_data()
    
    if data:
        save_data(data)
    else:
        print("Failed to scrape data") 