import os
import sys
import pandas as pd
from src.data.scraper import scrape_fighters, scrape_completed_events
from src.features.elo import process_fights

def main():
    print("Starting UFC Prediction System Pipeline...")

    # 1. Data Collection
    # Check if we need to scrape
    # For this demo, let's scrape if files don't exist

    if not os.path.exists('data/raw/fighters.csv'):
        print("Scraping fighters...")
        scrape_fighters(limit=5) # Limit to first 5 letters for speed in this demo
    else:
        print("Fighters data found. Skipping scrape.")

    if not os.path.exists('data/raw/fights.csv') or pd.read_csv('data/raw/fights.csv').empty:
        print("Scraping events...")
        # Scrape more events to get a decent history for ELO
        scrape_completed_events(limit=50)
    else:
        print("Fights data found. Skipping scrape.")

    # 2. Feature Engineering (ELO)
    print("Calculating ELO ratings...")
    process_fights('data/raw/fights.csv', 'data/processed/elo_ratings.csv')

    # 3. Output Results
    if os.path.exists('data/processed/elo_ratings.csv'):
        df = pd.read_csv('data/processed/elo_ratings.csv')
        print("\nTop 10 Fighters by ELO:")
        print(df.head(10))
    else:
        print("No ELO ratings generated.")

if __name__ == "__main__":
    main()
