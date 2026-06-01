import requests
from datetime import datetime
import json
import os

def fetch_bitcoin_data():
    """
    Fetch Bitcoin current data for today from CoinGecko API.
    Returns the API response or None if the request fails.
    """
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        params = {
            "localization": "false"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def extract_today_metrics(data):
    """
    Extract today's Bitcoin metrics from API data.
    Returns a dictionary with all metrics.
    """
    if not data:
        return None
    
    try:
        current_price = data["market_data"]["current_price"]["usd"]
        price_change_24h = data["market_data"]["price_change_24h"]
        price_change_percentage_24h = data["market_data"]["price_change_percentage_24h"]
        market_cap = data["market_data"]["market_cap"]["usd"]
        volume_24h = data["market_data"]["total_volume"]["usd"]
        
        return {
            "average_price": current_price,
            "price_change": price_change_24h,
            "percent_change": price_change_percentage_24h,
            "market_cap": market_cap,
            "volume": volume_24h,
            "current_price": current_price
        }
    except (KeyError, TypeError):
        return None

def save_to_file(metrics):
    """
    Save Bitcoin data to a file line by line if it doesn't already exist.
    Creates the file if it doesn't exist.
    """
    filename = "bitcoin_pricing_data.txt"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Format each line of data
    lines = [
        f"Date: {today}",
        f"Price Change: ${metrics['price_change']:,.2f} ({metrics['percent_change']:.2f}%)",
        f"Market Cap: ${metrics['market_cap']:,.0f}",
        f"Volume: ${metrics['volume']:,.0f}",
        "-" * 60
    ]
    
    # Check if file exists and if today's data already exists
    data_exists = False
    if os.path.exists(filename):
        with open(filename, "r") as file:
            content = file.read()
        if f"Date: {today}" in content:
            data_exists = True
            print(f"Data for {today} already exists in {filename}. Skipping append.")
            return
    
    # Append data to file line by line
    with open(filename, "a") as file:
        for line in lines:
            file.write(line + "\n")
        file.write("\n")
    
    print(f"Data saved to {filename}")

def display_metrics(metrics):
    """
    Display Bitcoin metrics for today in a formatted console output.
    """
    if not metrics:
        print("No data available.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "=" * 60)
    print("BITCOIN DATA - TODAY")
    print("=" * 60)
    print(f"Date:             {today}")
    print(f"Price Change:     ${metrics['price_change']:,.2f} ({metrics['percent_change']:.2f}%)")
    print(f"Market Cap:       ${metrics['market_cap']:,.0f}")
    print(f"Volume:           ${metrics['volume']:,.0f}")
    print("=" * 60 + "\n")

def main():
    """
    Main function to orchestrate Bitcoin data fetching and display for today.
    """
    print("Fetching Bitcoin data for today...")
    
    # Fetch data from API
    api_data = fetch_bitcoin_data()
    
    if api_data is None:
        print("Failed to retrieve data. Exiting.")
        return
    
    # Extract today's metrics
    metrics = extract_today_metrics(api_data)
    
    # Display results
    display_metrics(metrics)
    
    # Save to file
    save_to_file(metrics)

if __name__ == "__main__":
    main()


